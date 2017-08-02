#!/usr/bin/perl
package Numbers_FI;

use strict 'vars';

# The Numbers package is used to convert numbers to written Finnish
# form with the desired inflectional form.

# You can add inflections here.  Note that the names of the forms must
# conform regular expression "[A-Z]+". Note that a special symbols !
# and " are used for ordinal versions of 1 and 2.  

# Currently supported inflections:
# ERI = 0567 -> nolla viisi kuusi seitsemän
# NOM = nominatiivi (viisi)
# GEN = genetiivi (viiden)
# ADE = adessiivi (viidellä) 
# ILL = illatiivi (viiteen) 
# PAR = partitiivi (viittä) 
# TRA = translatiivi (viideksi)
# INE = inessiivi (viidessä)
# JNOM = järjestys nominatiivi (viides)

my %inflections = ("NOM", {"0", "nolla", "1", "yksi", "2", "kaksi",
			   "3", "kolme", "4", "neljä", "5", "viisi",
			   "6", "kuusi", "7", "seitsemän", "8",
			   "kahdeksan", "9", "yhdeksän", "o",
			   "toista", "k", "kymmenen", "s", "sata",
			   "t", "tuhat", "m", "miljoon", "r",
			   "miljardi", "b", "biljoona" },

		   "GEN", {"1", "yhden", "2", "kahden", "3", "kolmen",
			   "4", "neljän", "5", "viiden", "6",
			   "kuuden", "7", "seitsemän", "8",
			   "kahdeksan", "9", "yhdeksän", "o",
			   "toista", "k", "kymmenen", "s", "sadan",
			   "t", "tuhannen", "m", "miljoonan", "r",
			   "miljardin", "b", "biljoonan" },

		   "ADE", {"1", "yhdellä", "2", "kahdella", "3",
			   "kolmella", "4", "neljällä", "5", "viidellä",
			   "6", "kuudella", "7", "seitsemällä", "8",
			   "kahdeksalla", "9", "yhdeksällä", "o",
			   "toista", "k", "kymmenellä", "s", "sadalla",
			   "t", "tuhannella", "m", "miljoonalla", "r",
			   "miljardilla", "b", "biljoonalla" },

		   "ILL", {"1", "yhteen", "2", "kahteen", "3",
			   "kolmeen", "4", "neljään", "5", "viiteen",
			   "6", "kuuteen", "7", "seitsemään", "8",
			   "kahdeksaan", "9", "yhdeksään", "o",
			   "toista", "k", "kymmeneen", "s", "sataan",
			   "t", "tuhanteen", "m", "miljoonaan", "r",
			   "miljardiin", "b", "biljoonaan" },

		   "PAR", {"1", "yhtä", "2", "kahta", "3", "kolmea", "4",
			   "neljää", "5", "viittä", "6", "kuutta", "7",
			   "seitsemää", "8", "kahdeksaa", "9",
			   "yhdeksää", "o", "toista", "k", "kymmentä",
			   "s", "sataa", "t", "tuhatta", "m",
			   "miljoonaa", "r", "miljardia", "b",
			   "biljoonaa" },

		   "TRA", {"1", "yhdeksi", "2", "kahdeksi", "3",
			   "kolmeksi", "4", "neljäksi", "5",
			   "viideksi", "6", "kuudeksi", "7",
			   "seitsemäksi", "8", "kahdeksaksi", "9",
			   "yhdeksäksi", "o", "toista", "k",
			   "kymmeneksi", "s", "sadaksi", "t",
			   "tuhanneksi", "m", "miljoonaksi", "r",
			   "miljardiksi", "b", "biljoonaksi" },

		   "INE", {"1", "yhdessä", "2", "kahdessa", "3",
			   "kolmessa", "4", "neljässä", "5",
			   "viidessä", "6", "kuudessa", "7",
			   "seitsemässä", "8", "kahdeksassa", "9",
			   "yhdeksässä", "o", "toista", "k",
			   "kymmenessä", "s", "sadassa", "t",
			   "tuhannessa", "m", "miljoonassa", "r",
			   "miljardissa", "b", "biljoonassa" },

		   "JNOM", {"!", "ensimmäinen", "\"", "toinen", "1",
			    "yhdes", "2", "kahdes", "3", "kolmas", "4",
			    "neljäs", "5", "viides", "6", "kuudes", "7",
			    "seitsemäs", "8", "kahdeksas", "9",
			    "yhdeksäs", "o", "toista", "k", "kymmenes",
			    "s", "sadas", "t", "tuhannes", "m",
			    "miljoonas", "r", "miljardis", "b",
			    "biljoonas" }, 

		   "JPAR", {"1", "yhdettä", "2", "kahdetta", "3",
			   "kolmannetta", "4", "neljättä", "5",
			   "viidettä", "6", "kuudetta", "7",
			   "seitsemättä", "8", "kahdeksatta", "9",
			   "yhdeksättä", "o", "toista", "k",
			   "kymmenettä", "s", "sadatta", "t",
			   "tuhannetta", "m", "miljoonatta", "r",
			   "miljarditta", "b", "biljoonatta", "!",
			   "ensimmäistä", "\"", "toista" }, 

		   );

# Encodings for different units (ones, tens, hunderds, etc...)
my %units = (0, "y", 1, "k", 2, "s", 3, "t", 6, "m", 9, "r", 12, "b");

##################################################
# convert(number) 
#
# Converts a number to the written form.  
# Parameters: 
# - number: The number to convert with an optional form: 100PAR

sub convert {
    my $number = shift;
    $number =~ s/(\d+)\#([A-Z]+)/$1/g;
    my $form = $2;
    $form = "NOM" if ($form eq "");


    # Just separate digits?
    $form = "ERI" if ($number =~ /^0/ || length($number) > 12);
    if ($form eq "ERI") {
	$number =~ s/[0-9]/$inflections{"NOM"}->{$&} . " "/ge;
	return $number;
    }

    my @digits = split(//, $number);

    # Encode the number in a string for later processing
    my $result = " ";
    my $place = scalar @digits;
    for my $d (@digits) {
	$place--;
	$result .= "$d";
	$result .= $units{$place % 3};
	$result .= "$units{$place} " if ($place > 2 && $place % 3 == 0);
    }

    # Convert teens
    $result =~ s/1k(\d)y/$1o/g;
    $result =~ s/0o/1k/g;

    # Remove redundant zeros and ones
    $result =~ s/0[a-z]\s*//g;
    $result =~ tr/y//d;
    $result =~ s/1([kstmrb])/$1/g;

    # Add inflectional forms
    $result =~ s/(\S)/$1$form/g;
    $result =~ s/(?<=NOM|PAR)([kstmrb])NOM/$1PAR/g;

    # Fix "ensimmäinen" and "toinen".
    $result =~ s/1(J[A-Z]+)$/!$1/g;
    $result =~ s/2(J[A-Z]+)$/\"$1/g;

    # Convert to the written form
    $result =~ s/([0-9a-z\"\!])([A-Z]{3,4})/$inflections{$2}->{$1}/ge;
    $result =~ tr/ //d;

    return $result;
}
