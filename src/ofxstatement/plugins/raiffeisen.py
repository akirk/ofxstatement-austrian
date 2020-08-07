#!/usr/bin/env python3
# This file is part of ofxstatement-austrian.
# See README.rst for more information.

import csv
import re
from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import generate_transaction_id, BankAccount
from ofxstatement.plugins.utils import \
    clean_multiple_whitespaces, fix_amount_string


class RaiffeisenCsvParser(CsvStatementParser):
    """The csv parser for Raiffeisen."""

    date_format = "%d.%m.%Y"

    mappings = {
        "date": 0,
        "memo": 1,
        "amount": 3,
        }

    def parse(self):
        """Parse."""
        stmt = super(RaiffeisenCsvParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Split records using a custom dialect."""
        return csv.reader(self.fin, delimiter=";")

    def parse_record(self, line):
        """Parse a single record."""
        # Currency
        if not self.statement.currency:
            self.statement.currency = line[4]

        # Cleanup parts
        line[3] = fix_amount_string(line[3])
        line[1] = clean_multiple_whitespaces(line[1])

        memo = re.split( r'((?:(?:BIC|IBAN) )?(?:Auftraggeber|Zahlungsempfänger|Empfänger)|Verwendungszweck|Zahlungsreferenz|Auftraggeberreferenz|Empfänger-Kennung|Mandat): ', line[1] )
        parsed_memo = {
            'Empfänger': re.sub(r'ONLINE BANKING VOM \d{2}.\d{2} UM \d{2}:\d{2}', '', re.sub(r'KONFORM \d+UEB\d+', '', memo.pop(0).replace( 'INTERNET-Überweisung', '')))
        }
        for k, v in zip(memo[::2], memo[1::2]):
            if ( k in parsed_memo ):
                parsed_memo[k] = (parsed_memo[k] + " " + v).strip()
            else:
                parsed_memo[k] = v.strip()

        # Create statement and fixup missing parts
        stmtline = super(RaiffeisenCsvParser, self).parse_record(line)
        stmtline.trntype = 'DEBIT' if stmtline.amount < 0 else 'CREDIT'
        stmtline.id = generate_transaction_id(stmtline)
        stmtline.payee = parsed_memo.get('Auftraggeber', parsed_memo.get('Zahlungsempfänger', parsed_memo.get('Empfänger')))
        stmtline.bank_account_to = BankAccount(
            parsed_memo.get('BIC Auftraggeber', parsed_memo.get('BIC Zahlungsempfänger', parsed_memo.get('BIC Empfänger'))),
            parsed_memo.get('IBAN Auftraggeber', parsed_memo.get('IBAN Zahlungsempfänger', parsed_memo.get('IBAN Empfänger')))
        )
        stmtline.check_no=parsed_memo.get('Auftraggeberreferenz')
        stmtline.memo=parsed_memo.get('Verwendungszweck',parsed_memo.get('Zahlungsreferenz',stmtline.memo))
        return stmtline


class RaiffeisenPlugin(Plugin):
    """Raiffeisenbank (CSV)"""

    def get_parser(self, filename):
        """Get a parser instance."""
        encoding = self.settings.get('charset', 'utf-8-sig')
        f = open(filename, 'r', encoding=encoding)
        parser = RaiffeisenCsvParser(f)
        parser.statement.account_id = self.settings.get('account', 'default')
        parser.statement.bank_id = self.settings.get('bank', 'Raiffeisen')
        return parser

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent
