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


from esr import ESR
from argparse import ArgumentParser    as ArgArgumentParser
from argparse import RawTextHelpFormatter as RawTextHelpFormatter


def run():
  parser=ArgArgumentParser(description='print readable content of a vesr file', formatter_class=RawTextHelpFormatter)
  parser.add_argument('file', help='Path to vesr file')
  args=parser.parse_args()


  with open(args.file, 'r') as f:
    data = f.read()

  statement = ESR.parse(data)

  for record in statement.records:
      for key in record.__dict__.keys():
        print('  {:30} :'.format(key)),
        print(getattr(record,key))
      print 

  print 'Total:'
  for key in statement.total_record.__dict__.keys():
        print('  {:30} :'.format(key)),
        print(getattr(statement.total_record,key))
