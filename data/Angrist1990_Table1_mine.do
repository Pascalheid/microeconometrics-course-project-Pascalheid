
cap log close
log using "DIRECTORY HERE\Angrist1990_Table1.log", replace

*************************************************************************
* PROGRAM: Angrist1990_Table1
* PROGRAMMER: Simone Schaner (sschaner@mit.edu)
* PURPOSE: Replicates table 1 from Angrist (1990)
* DATE CREATED: 7/23/07
* NOTE: Program as written produces corrected standard errors.
* To reproduce standard errors in publlished version of paper,
* comment out line 58 and uncomment line 59
************************************************************************

clear
set mem 50m
set more off

cd "C:\Users\Pascal\Desktop\Pascal\Uni\Master\4.Semester\microeconometrics-course-project-Pascalheid\data"

use cwhsa
	g type="TAXAB"

append using cwhsb

* LOOK AT DATA
des *
sum *

*  ONLY KEEP BIRTH COHORTS 1950-1953
keep if byr>=50

* ONLY KEEP YEARS ABOVE 1965
keep if year>65

* DRAFT ELIGIBLE
g byte eligible=0
	replace eligible=1 if (byr>=44 & byr<=50 & interval<=39) /*CUTOFF=195*/
	replace eligible=1 if byr==51 & interval<=25 /*CUTOFF=125*/
	replace eligible=1 if (byr==52 | byr==53) & interval<=19  /*CUTOFF=95*/

 *  RACE DUMMIES
g byte white= race==1
g byte nonwhite= race==2

* DIFFERENT WEIGHTS AND MEANS FOR NONZEROS ONLY
g earn_nz= vmn1/(1-vfin1)
g wt_nz= vnu1*(1-vfin1)

* TAG FICA OBS
g byte fica= type=="TAXAB"

egen collby= group(white byr year eligible fica)

* SOME CALCULATIONS FOR STANDARD ERRORS
	g var= vsd1^2
	* VARIANCE OF NONZERO CELLS
	* var_nz= (vnu1*(var+vmn1^2)-wt_nz*earn_nz^2)/wt_nz
	* !!!! USE THIS  VERSION TO REPRODUCE SEs IN PUBLISHED TABLE 1 OF ANGRIST (1990) !!!!!
	g var_nz= var * (vnu1 / wt_nz)
	* SUM WEIGHTS ACROSS GROUP CELLS
	egen sumwt=sum(wt_nz), by(collby)

	* WEIGHT FOR VARIANCE
	g wtmult= 1/(sumwt) /*WOULD USE THIS ONE W/ UNWEIGHTED COLLAPSE SUM STATEMENT -- wt_nz/(sumwt)^2*/

	* VARIANCE TO SUM
	g var_cm= wtmult*var_nz

*************** Got it until here **

collapse (mean) var_cm earn_nz white year byr eligible fica [w=wt_nz], by(collby)
	g fica2="f" if fica==1
		replace fica2="w" if fica==0

drop collby
egen id= concat(white year eligible fica)
reshape wide var_cm earn_nz, i(id) j(byr)

drop id
egen id= concat(white year fica)
reshape wide var_cm* earn_nz*, i(id) j(eligible)

drop id
drop fica

egen id= concat(white year)
reshape wide var_cm* earn_nz*, i(id) j(fica2) string

* GET DIFFERENCES AND STANDARD ERRORS, PUT IN TABLE FORMAT

	foreach num in 50 51 52 53 {
		g c19`num'f= earn_nz`num'1f-earn_nz`num'0f
		g se19`num'f=(var_cm`num'1f+var_cm`num'0f)^.5
		g c19`num'w= earn_nz`num'1w-earn_nz`num'0w
		g se19`num'w=(var_cm`num'1w+var_cm`num'0w)^.5
		}

	keep year white c19* se19*
	expand 2
	sort year

	mkmat year c19* se19* if white, matrix(whites1)
	mkmat year c19* se19* if white==0, matrix(nonwhites1)

	mat whites=J(rowsof(whites1),9,0)
	mat nonwhites=J(rowsof(nonwhites1),9,0)

	local top=rowsof(whites1)
	local top1=`top'-1

	foreach mat in whites nonwhites {
		mat colnames `mat' = year 1950f 1951f 1952f 1953f 1950w 1951w 1952w 1953w
		}

foreach mat in whites nonwhites {
	forval val=1(2)`top1' {
		mat `mat'[`val',1]=`mat'1[`val',"year"]
		mat `mat'[`val',2]=`mat'1[`val',"c1950f"]
		mat `mat'[`val',3]=`mat'1[`val',"c1951f"]
		mat `mat'[`val',4]=`mat'1[`val',"c1952f"]
		mat `mat'[`val',5]=`mat'1[`val',"c1953f"]
		mat `mat'[`val',6]=`mat'1[`val',"c1950w"]
		mat `mat'[`val',7]=`mat'1[`val',"c1951w"]
		mat `mat'[`val',8]=`mat'1[`val',"c1952w"]
		mat `mat'[`val',9]=`mat'1[`val',"c1953w"]
		}

	forval val=2(2)`top' {
		mat `mat'[`val',1]=.
		mat `mat'[`val',2]=`mat'1[`val',"se1950f"]
		mat `mat'[`val',3]=`mat'1[`val',"se1951f"]
		mat `mat'[`val',4]=`mat'1[`val',"se1952f"]
		mat `mat'[`val',5]=`mat'1[`val',"se1953f"]
		mat `mat'[`val',6]=`mat'1[`val',"se1950w"]
		mat `mat'[`val',7]=`mat'1[`val',"se1951w"]
		mat `mat'[`val',8]=`mat'1[`val',"se1952w"]
		mat `mat'[`val',9]=`mat'1[`val',"se1953w"]
		}
		}

* DISPLAY TABLES -- THESE SHOW COEFFS WITH SEs BELOW IN SAME FORMAT AS TABLE 1 IN AER PAPER
	mat li whites
	mat li nonwhites

log close
