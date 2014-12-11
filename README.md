gnucash-toolset
===============

Access and manipulate gnucash data.

usage: gnucash-toolset [-h]
                       {csv-vendors,create-copy,csv-customers} in_file
                       out_file

Gnucash toolset to export/manipulate gnucash data

positional arguments:
  {csv-vendors,create-copy,csv-customers}
     Commands to execute:
     csv-customers  : Create a CSV file with all customers. Ready to import with gnucash.
     csv-vendors    : Create a CSV file with all vendors. Ready to import with gnucash.
     create-copy    : Create a copy of gnucash data. Data copied are: Accounts, Customers, Vendors.
                      Data NOT copied: Bookings, Invoices, Bills.
                      Data to be copied, but not yet implemented: Terms, Taxes, Employees, Options.
                      This can be used to create a new file after closing period.
  in_file               Path to gnucash file to take out values
  out_file              Path/file for output

optional arguments:
  -h, --help            show this help message and exit


