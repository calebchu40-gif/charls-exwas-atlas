/*
  Synthetic-only exporter for the official CHARLS lunar2solar lookup.

  Run from Stata with:
    do scripts/export_charls_lunar2solar_official_grid.do "<project-root>" "<output-csv>"

  It creates every syntactically possible YYYYMMDD key from 1900-01-01 through
  2040-12-31, then asks the pinned CHARLS ado/mata table for ordinary and leap
  mappings. Only synthetic dates are used; no CHARLS participant data is read.
*/
version 15.1
args project_root output_csv

if `"`project_root'"' == "" | `"`output_csv'"' == "" {
    display as error "Usage: do scripts/export_charls_lunar2solar_official_grid.do <project-root> <output-csv>"
    exit 198
}

local src `"`project_root'/references/charls_lunar2solar/src"'
capture confirm file `"`src'/lunar2solar.ado"'
if _rc {
    display as error "Pinned CHARLS lunar2solar.ado was not found under project-root."
    exit 601
}
capture confirm file `"`src'/lunar2solar.mmat"'
if _rc {
    display as error "Pinned CHARLS lunar2solar.mmat was not found under project-root."
    exit 601
}

tempfile work candidate
local personal `"`work'/personal"'
capture mkdir `"`work'"'
capture mkdir `"`personal'"'
copy `"`src'/lunar2solar.mmat"' `"`personal'/lunar2solar.mmat"', replace
sysdir set PERSONAL `"`personal'"'
do `"`src'/lunar2solar.ado"'

clear
set obs 52452
gen int year = 1900 + floor((_n - 1) / (12 * 31))
gen byte month = mod(floor((_n - 1) / 31), 12) + 1
gen byte day = mod(_n - 1, 31) + 1
gen str8 lunar_date = string(year, "%04.0f") + string(month, "%02.0f") + string(day, "%02.0f")
keep lunar_date
isid lunar_date
save `"`candidate'"', replace

lunar2solar lunar_date, generate(solar_ordinary)
lunar2solar lunar_date, leap generate(solar_leap)
keep lunar_date solar_ordinary solar_leap
export delimited using `"`output_csv'"', replace
display as result "Exported synthetic official lookup grid only; no participant records were accessed."

capture erase `"`personal'/lunar2solar.mmat"'
capture rmdir `"`personal'"'
capture rmdir `"`work'"'
