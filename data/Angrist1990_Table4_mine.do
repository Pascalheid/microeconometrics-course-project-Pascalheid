
 cap log close
 log using log using "INSERT DIRECTORY HERE\Angrist1990_Table4.log", replace

*************************************************
* PROGRAM: Angrist1990_Table4
* PROGRAMMER: Simone Schaner
* PURPOSE: Replicates table 4 from Angrist (1990)
* DATE CREATED: 7/24/07
* NOTES: You must be running STATA 9+ for this
* 	 code to work (uses MATA)
*	To reproduce values in published paper,
*	 uncomment lines 26 and 27
*************************************************

clear
set mem 50m
set more off
set matsize 8000

cd "C:\Users\Pascal\Desktop\Pascal\Uni\Master\4.Semester\microeconometrics-course-project-Pascalheid\data"

use cwhsc_new

* UNCOMMENT TO USE OLD WEIGHTS
drop iweight
ren iweight_old iweight

* LOOK AT DATA
des *
sum *

keep if year>=81
g tctr=1 if type=="TAXAB"
	replace tctr=2 if type=="ADJ"
	replace tctr=3 if type=="TOTAL"

* YEAR DUMMIES
qui tab year, ge(yrdum)
qui tab byr, ge(byrdum)

g ps_r50= ps_r*(byr==50)
g ps_r51= ps_r*(byr==51)
g ps_r52= ps_r*(byr==52)
g ps_r53= ps_r*(byr==53)

***********************************************
* ALPHA ESTIMATES
***********************************************

g alpha1=-999
g alpha2=-999

* FOR POOLED REGRESSIONS
foreach race in 1 2 {
	foreach type in 1 2 3 {
	reg earnings byrdum1-byrdum3 yrdum2-yrdum4 ///
		ps_r if tctr==`type' & race==`race' [w=iweight]
	qui replace alpha1= _b[ps_r] if e(sample)
	}
	}

* FOR BY COHORT REGRESSIONS
foreach race in 1 2 {
	foreach type in 1 2 3 {
	reg earnings byrdum1-byrdum3 yrdum2-yrdum4 ps_r50-ps_r53 ///
		if tctr==`type' & race==`race' [w=iweight]
	qui replace alpha2= _b[ps_r50] if e(sample) & byr==50
	qui replace alpha2= _b[ps_r51] if e(sample) & byr==51
	qui replace alpha2= _b[ps_r52] if e(sample) & byr==52
	qui replace alpha2= _b[ps_r53] if e(sample) & byr==53
	}
	}

************************************************
************************************************
***********************************************************************************************************************************
cap prog drop sample
* search over rows and replace smpl by the sample size defined below as val
prog define sample
	args byr race val
	replace smpl=`val' if race==`race' & byr==`byr'
	end
g smpl=0

sample 50 1 351
sample 51 1 16744
sample 52 1 17662
sample 53 1 17694

sample 50 2 70
sample 51 2 5251
sample 52 2 5480
sample 53 2 5294

g term1= (alpha1^2)*ps_r*(1-ps_r)*(1/smpl)
g term2= (alpha2^2)*ps_r*(1-ps_r)*(1/smpl)

g byte intercep=1
g wts= 1/iweight^.5

 sort byr tctr race interval year

* MATRICES FOR TRANSFORMATION TO GLS

***********************************************************
		/*MATA - MUST BE USING STATA 9*/
***********************************************************
mata
* (5304x1)
st_view(Y=.,.,"earnings")
* (5304x8)
st_view(X1=.,.,("intercep", "byrdum1", "byrdum2", "byrdum3", /*
	*/ "yrdum2", "yrdum3", "yrdum4", "ps_r"))
* (5304x11)
st_view(X2=.,.,("intercep", "byrdum1", "byrdum2", "byrdum3", /*
	*/ "yrdum2", "yrdum3", "yrdum4", "ps_r50", "ps_r51", "ps_r52", "ps_r53"))
* (5304x5)
st_view(clss=.,.,("tctr", "byr", "race", "interval", "year"))
* (5304x4)
st_view(covmtrx=.,.,("ern81", "ern82", "ern83", "ern84"))
* (5304x1)
st_view(term1=.,.,"term1")
st_view(term2=.,.,"term2")
st_view(wtvec=.,.,"wts")

Y1_t= Y:*0:+-999
Y2_t= Y:*0:+-999
X1_t= X1:*0:-999
X2_t= X2:*0:-999

j=0

while (j<=1325) {

	* First four values of wts (4x1)
	wtvec_t= wtvec[|4*j+1,1 \ 4*j+4,1|]
	* first four rows of cov matrix (4x4)
	covmtrx_t= covmtrx[|4*j+1,1 \ 4*j+4,4|]
	* First four values of term 1 (4x1)
	term1_t= term1[|4*j+1,1 \ 4*j+4,1|]
	* First four values of term 2 (4x1)
	term2_t= term2[|4*j+1,1 \ 4*j+4,1|]

	*First four values of Y (4x1)
	Y_e= Y[|4*j+1,1 \ 4*j+4,1|]

	* First four rows of X1 (4x8)
	X1_e= X1[|4*j+1,1 \ 4*j+4,8|]
	* First four rows of X2 (4x11)
	X2_e= X2[|4*j+1,1 \ 4*j+4,11|]

	covmtrx1_t= wtvec_t:*covmtrx_t:*wtvec_t':+term1_t
	covmtrx2_t= wtvec_t:*covmtrx_t:*wtvec_t':+term2_t

	final1= cholesky(invsym(covmtrx1_t))
	final2= cholesky(invsym(covmtrx2_t))

	Y1_e= final1'*Y_e
	X1_e= final1'*X1_e

	Y2_e= final2'*Y_e
	X2_e= final2'*X2_e

	* Fill empty vectors and matrices
	Y1_t[|4*j+1,1\4*j+4,1|]=Y1_e
	X1_t[|4*j+1,1\4*j+4,8|]=X1_e

	Y2_t[|4*j+1,1\4*j+4,1|]=Y2_e
	X2_t[|4*j+1,1\4*j+4,11|]=X2_e

	j++

	}

	alldata1= (Y1_t,X1_t,clss)
	alldata2= (Y2_t,X2_t,clss)

	st_matrix("alldata1",alldata1)
	st_matrix("alldata2",alldata2)

	end
*********************************************************
				/* END MATA */
*********************************************************


mat colnames alldata1= earnings intercept bd1 bd2 bd3 ///
	yd2 yd3 yd4 ps_r tctr byr race interval year
mat colnames alldata2= earnings intercept bd1 bd2 bd3 ///
	yd2 yd3 yd4 ps_r50 ps_r51 ps_r52 ps_r53 tctr byr race interval year

drop _all

mat whites=J(16,3,.)
mat nonwhites=J(16,3,.)
	mat colnames whites= "FICA Taxable Earnings" "Adjusted Fica Earnings" ///
		"Total W-2 Compensation"
	mat colnames nonwhites= "FICA Taxable Earnings" "Adjusted Fica Earnings" ///
		"Total W-2 Compensation"
	mat rownames whites= "Model1" 1950 " " 1951 " " 1952 " " 1953 " " "X2(873)" ///
		" " "Model 2" "1950-53" " " " " "X2(876)
	mat rownames nonwhites= "Model1" 1950 " " 1951 " " 1952 " " 1953 " " "X2(873)" ///
		" " "Model 2" "1950-53" " " " " "X2(876)

* FIRST DO POOLED COHORTS
svmat alldata1, names(col)

forval type=1/3 {
* WHITES
reg earnings intercep bd1-bd3 yd2-yd4 ps_r if tctr==`type' & race==1, nocons
	mat whites[13,`type']= round(_b[ps_r],.1)
	mat whites[14,`type']= round(_se[ps_r]/e(rmse),.1)
	mat whites[16,`type']= round(e(rss),.1)

* NONWHITES
reg earnings intercep bd1-bd3 yd2-yd4 ps_r if tctr==`type' & race==2, nocons
	mat nonwhites[13,`type']= round(_b[ps_r],.1)
	mat nonwhites[14,`type']= round(_se[ps_r]/e(rmse),.1)
	mat nonwhites[16,`type']= round(e(rss),.1)
}

* NEXT INDIVIDUAL COEFFS
drop _all
svmat alldata2, names(col)

forval type=1/3 {
* WHITES
qui reg earnings intercep bd1-bd3 yd2-yd4 ps_r50-ps_r53 if tctr==`type' & race==1, nocons
	mat whites[2,`type']= round(_b[ps_r50],.1)
	mat whites[3,`type']= round(_se[ps_r50]/e(rmse),.1)
	mat whites[4,`type']= round(_b[ps_r51],.1)
	mat whites[5,`type']= round(_se[ps_r51]/e(rmse),.1)
	mat whites[6,`type']= round(_b[ps_r52],.1)
	mat whites[7,`type']= round(_se[ps_r52]/e(rmse),.1)
	mat whites[8,`type']= round(_b[ps_r53],.1)
	mat whites[9,`type']= round(_se[ps_r53]/e(rmse),.1)
	mat whites[10,`type']= round(e(rss),.1)

* NONWHITES
qui reg earnings intercep bd1-bd3 yd2-yd4 ps_r50-ps_r53 if tctr==`type' & race==2, nocons
	mat nonwhites[2,`type']= round(_b[ps_r50],.1)
	mat nonwhites[3,`type']= round(_se[ps_r50]/e(rmse),.1)
	mat nonwhites[4,`type']= round(_b[ps_r51],.1)
	mat nonwhites[5,`type']= round(_se[ps_r51]/e(rmse),.1)
	mat nonwhites[6,`type']= round(_b[ps_r52],.1)
	mat nonwhites[7,`type']= round(_se[ps_r52]/e(rmse),.1)
	mat nonwhites[8,`type']= round(_b[ps_r53],.1)
	mat nonwhites[9,`type']= round(_se[ps_r53]/e(rmse),.1)
	mat nonwhites[10,`type']= round(e(rss),.1)
	}

mat li whites
mat li nonwhites

log close

