
cap log close
log using "INSERT DIRECTORY HERE\Angrist1990_Table2DMDC.log", replace

*************************************************************************
* PROGRAM: Angrist1990_Table2DMDC
* PROGRAMMER: Simone Schaner
* PURPOSE: Reproduces DMDC portion of table 2 of Angrist (1990)
* DATE CREATED: 7/26/07
************************************************************************

clear
set mem 50m
set more off

cd "INSERT DIRECTORY HERE"

* FIRST GET SUMMED DATA BY COHORT AND RACE FROM CHWS

use cwhsa
	keep if byr>=51 /*CANNOT USE FOR 1950*/
	keep if year==70


* DRAFT ELIGIBLE
g byte eligible=0
	replace eligible=1 if (byr>=44 & byr<=50 & interval<=39) /*CUTOFF=195*/
	replace eligible=1 if byr==51 & interval<=25 /*CUTOFF=125*/
	replace eligible=1 if (byr==52 | byr==53) & interval<=19  /*CUTOFF=95*/

collapse (sum) vnu1, by(race byr year eligible)
	sort race  byr eligible
tempfile cwhs
	save "`cwhs'"


clear

use dmdcdat

g byte eligible=0
	replace eligible=1 if (byr>=44 & byr<=50 & interval<=39) /*CUTOFF=195*/
	replace eligible=1 if byr==51 & interval<=25 /*CUTOFF=125*/
	replace eligible=1 if (byr==52 | byr==53) & interval<=19  /*CUTOFF=95*/

collapse (sum) nsrvd, by(race byr eligible)

sort race byr eligible

merge race byr eligible using "`cwhs'"
	drop _merge

egen nsrvd_all= sum(nsrvd), by(race byr)
egen vnu1_all= sum(vnu1), by(race byr)

* PROPORTION VETERAN
g p_vet= nsrvd/(vnu1*100)
g p_vetall= nsrvd_all/(vnu1_all*100)

* STANDARD ERRORS/VARIANCE
g se_vet= ((p_vet*(1-p_vet))/vnu1)^.5
g se_vet_all= ((p_vetall*(1-p_vetall))/vnu1_all)^.5


mat mat1= J(6,5,.)
mat mat2=J(6,5,.)

mat colnames mat1=  Sample P(Veteran) phat_e phat_n "phat_e-phat_n"
mat colnames mat2=  Sample P(Veteran) phat_e phat_n "phat_e-phat_n"

mat rownames mat1= 1951 " " 1952 " " 1953 " "
mat rownames mat2= 1951 " " 1952 " " 1953 " "

replace byr=byr-50

forval race=1/2 {
	forval byr=1/3 {
		qui sum vnu1_all if race==`race' & byr==`byr'
			mat mat`race'[(`byr'-1)*2+1,1]=r(mean)
		qui sum p_vetall if race==`race' & byr==`byr'
			mat mat`race'[(`byr'-1)*2+1,2]=r(mean)
		qui sum p_vet if race==`race' & byr==`byr' & elig==1
			mat mat`race'[(`byr'-1)*2+1,3]=r(mean)
		qui sum p_vet if race==`race' & byr==`byr' & elig==0
			mat mat`race'[(`byr'-1)*2+1,4]=r(mean)
		mat mat`race'[(`byr'-1)*2+1,5]= mat`race'[(`byr'-1)*2+1,3]-mat`race'[(`byr'-1)*2+1,4]

		qui sum se_vet_all if race==`race' & byr==`byr'
			mat mat`race'[`byr'*2,2]=r(mean)
		qui sum se_vet if race==`race' & byr==`byr' & elig==1
			mat mat`race'[`byr'*2,3]=r(mean)
		qui sum se_vet if race==`race' & byr==`byr' & elig==0
			mat mat`race'[`byr'*2,4]=r(mean)
		mat mat`race'[`byr'*2,5]=((mat`race'[`byr'*2,3])^2+(mat`race'[`byr'*2,4])^2)^.5
		}
		}

* WHITES
	mat li mat1

* NONWHITES
	mat li mat2

log close


