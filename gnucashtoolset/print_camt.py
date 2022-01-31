#
#    Copyright (C) 2014  Cirrax GmbH  http://www.cirrax.com
#    Benedikt Trefzer <benedikt.trefzer@cirrax.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   


import xml.etree.ElementTree
from argparse import ArgumentParser    as ArgArgumentParser
from argparse import RawTextHelpFormatter as RawTextHelpFormatter


def run():
  parser=ArgArgumentParser(description='print readable content of a camt file', formatter_class=RawTextHelpFormatter)
  parser.add_argument('file', help='Path to camt file')
  args=parser.parse_args()


  x = {'s': 'urn:iso:std:iso:20022:tech:xsd:camt.054.001.04'}
  e = xml.etree.ElementTree.parse(args.file).getroot()

  for notification in e.findall('./s:BkToCstmrDbtCdtNtfctn/s:Ntfctn/s:Ntry',x ):
    try:
      info = notification.find('./s:AddtlNtryInf',x).text
      print('Header:       {}'.format(' '.join(info.split())))
    except:
      print('Header:       {}'.format('no info'))
    print('booking date: {}'.format(notification.find('./s:BookgDt/s:Dt',x).text))
    print('valuta date:  {}'.format(notification.find('./s:ValDt/s:Dt',x).text))
    print('total amount: {}'.format(notification.find('./s:Amt',x).text))
    print('===============')

    for detail in notification.findall('./s:NtryDtls/s:TxDtls',x ):
      print('typ:          {}'.format(detail.find('./s:Refs/s:Prtry/s:Tp',x).text))
      print('ref:          {}'.format(detail.find('./s:Refs/s:Prtry/s:Ref',x).text))
      print('amount:       {}'.format(detail.find('./s:Amt',x).text))
      print('refnum:       {}'.format(detail.find('./s:RmtInf/s:Strd/s:CdtrRefInf/s:Ref',x).text))
      print('debitor:      {}'.format(detail.find('./s:RltdPties/s:Dbtr/',x).text))
      try:
        print('debitor IBAN: {}'.format(detail.find('./s:RltdPties/s:DbtrAcct/s:Id/s:IBAN',x).text))
      except:
        print('debitor IBAN: {}'.format('unknown'))
      print('---------------')
