
cap log close
log using "DIRECTORY HERE\Angrist1990_Table3.log, replace

*************************************************************************
* PROGRAM: Angrist1990_Table3.do
* PROGRAMMER: Simone Schaner (sschaner@mit.edu)
* PURPOSE: Replicates table 3 from Angrist (1990)
* DATE CREATED: 7/26/07
* NOTE: To reproduce table results, uncomment lines 23 and 24. Results for
*	column 5 vary slightly from published values.
************************************************************************

clear
set mem 50m
set more off
cd "DIRECTORY HERE"


use cwhsc_new

* UNCOMMENT TO USE UNADJUSTED WEIGHTS
* drop iweight
* ren iweight_old iweight

* MERGE ON CPI INFO TO GO BACK TO REAL VALUES
	sort year
	merge year using cpi_angrist1990
		drop _merge

qui sum cpi if year==78
	local cpi78=r(mean)

replace cpi=cpi/`cpi78'
	replace cpi=round(cpi,.001) /*TO MATCH ORIGINAL DEFLATION*/
g cpi2= cpi^2
g smplsz= nj-nj0 /*NUMBER NONZEROS IN CELLS*/

keep if year>=81
*  ONLY KEEP BIRTH COHORTS 1950-1952
keep if byr>=50 & byr<=52

* BACK OUT VARIANCE FROM IWEIGHTS
g rlvar= (1/iweight)*smplsz
g var= rlvar*cpi2

* MAKE REAL EARNINGS
g nomearn= (earnings*cpi)

* SAME PROCESS AS TABLE 1 TO OBTAIN POINT ESTIMATES OF DIFFERENCES

* DRAFT ELIGIBLE
g byte eligible=0
	replace eligible=1 if byr==50 & interval==1 /*CUTOFF=195 -- recoded to 2 intervals here*/
	replace eligible=1 if byr==51 & interval<=25 /*CUTOFF=125*/
	replace eligible=1 if (byr==52 | byr==53) & interval<=19  /*CUTOFF=95*/

* RACE
g byte white= race==1

* GROUPS TO COLLAPSE BY
egen collby= group(white byr year eligible type)

* SUM WEIGHTS ACROSS GROUP CELLS
	egen sumwt= sum(smplsz), by(collby)

* WEIGHT FOR VARIANCE
	g wtmult= 1/(sumwt) /*WOULD USE THIS ONE W/ UNWEIGHTED COLLAPSE SUM STATEMENT -- wt_nz/(sumwt)^2*/

* VARIANCE TO SUM
	g var_cm= wtmult*var

g numtype= 1 if type=="TAXAB"
	replace numtype=2 if type=="ADJ"
	replace numtype=3 if type=="TOTAL"

collapse (mean) var_cm nomearn earnings cpi [w=smplsz], by(white byr year eligible numtype)

egen id= concat(white year numtype byr)
reshape wide var_cm* nomearn* earnings*, i(id) j(eligible)

drop id

g tag= "f" if numtype==1
	replace tag= "a" if numtype==2
	replace tag= "w" if numtype==3

	drop numtype
egen id= concat(white year byr)
reshape wide var_cm* nomearn* earnings*, i(id) j(tag) string



		g cf= nomearn1f-nomearn0f
		g sef=(var_cm1f+var_cm0f)^.5
		g cw= nomearn1w-nomearn0w
		g sew=(var_cm1w+var_cm0w)^.5
		g ca= nomearn1a-nomearn0a
		g sea=(var_cm1a+var_cm0a)^.5


	keep year byr white c* se*

expand 2
	sort byr year

* IMPUTE SIPP PROBABILITIES --- SEE CODE FOR TABLE 2 TO RECREATE NUMBERS
g sippp= .159 if byr==50
	replace sippp= .136 if byr==51
	replace sipp= .105 if byr==52

g sippse= .040 if byr==50
	replace sippse= .043 if byr==51
	replace sippse= .050 if byr==52

g serv_c= ca/(sippp*cpi)
g serv_se= sea/(sippp*cpi)

	mkmat year c* se* sipp* serv* if white, matrix(whites1)
	mkmat year c* se* sipp* serv* if white==0, matrix(nonwhites1)

	mat whites=J(rowsof(whites1),7,.)
	mat nonwhites=J(rowsof(nonwhites1),7,.)

		local top=rowsof(whites1)
	local top1=`top'-1

	foreach mat in whites nonwhites {
		mat colnames `mat' = "Cohort" "Year" "FICA" "Adj FICA" ///
			"W-2"	"pe-pn" "Serv Eff"
		}


foreach mat in whites nonwhites {
	forval val=1(2)`top1' {
		mat `mat'[`val',2]=`mat'1[`val',"year"]
		mat `mat'[`val',3]=`mat'1[`val',"cf"]
		mat `mat'[`val',4]=`mat'1[`val',"ca"]
		mat `mat'[`val',5]=`mat'1[`val',"cw"]
		mat `mat'[`val',7]=`mat'1[`val',"serv_c"]
		}

	forval val=2(2)`top' {
		mat `mat'[`val',3]=`mat'1[`val',"sef"]
		mat `mat'[`val',4]=`mat'1[`val',"sea"]
		mat `mat'[`val',5]=`mat'1[`val',"sew"]
		mat `mat'[`val',7]=`mat'1[`val',"serv_se"]
		}

		mat `mat'[1,1]=1950
		mat `mat'[9,1]=1951
		mat `mat'[17,1]=1952

		mat `mat'[1,6]=.159
		mat `mat'[2,6]=.040
		mat `mat'[9,6]=.136
		mat `mat'[10,6]=.043
		mat `mat'[17,6]=.105
		mat `mat'[18,6]=.050
		}



	mat li whites
	mat li nonwhites

log close