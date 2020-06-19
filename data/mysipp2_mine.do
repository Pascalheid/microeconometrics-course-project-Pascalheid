*************************************************
* This program generates the SIPP (84) panel 	*
* of Table 2 in Angrist (1990)			*
*************************************************
clear
cd "C:\Users\Pascal\Desktop\Pascal\Uni\Master\4.Semester\microeconometrics-course-project-Pascalheid\data"

use sipp2.dta


*Unconditional P(Veteran):
forvalues race=0/1 {
	forvalues year=1950/1953 {
  		quietly reg nvstat if u_brthyr>=`year'-1 & ///
		u_brthyr<=`year'+1 & nrace==`race' ///
		[aweight=fnlwgt_5]
		display ""
		display "year = `year', race = `race':"
		display _b[_cons]
		display _se[_cons]
		display e(N)
  	}
}

*P(Veteran|eligible):
forvalues race=0/1 {
	forvalues year=1950/1953 {
  		quietly reg nvstat if u_brthyr>=`year'-1 & ///
		u_brthyr<=`year'+1 & nrace==`race' & rsncode==1 ///
		[aweight=fnlwgt_5]
		display ""
		display "year = `year', race = `race':"
		display _b[_cons]
		display _se[_cons]
		display e(N)
  	}
}
*P(Veteran|ineligible):
forvalues race=0/1 {
	forvalues year=1950/1953 {
  		quietly reg nvstat if u_brthyr>=`year'-1 & ///
		u_brthyr<=`year'+1 & nrace==`race' & rsncode~=1 ///
		[aweight=fnlwgt_5]
		display ""
		display "year = `year', race = `race':"
		display _b[_cons]
		display _se[_cons]
		display e(N)
  	}
}
