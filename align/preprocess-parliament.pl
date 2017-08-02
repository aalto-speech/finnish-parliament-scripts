#!/usr/bin/perl
use File::Basename;
use lib dirname (__FILE__);
use Numbers_FI;
use locale;

while (<>) 
{
    # Remove headers and footers   
    if (/SPEAKER:*/)
    {
       print "$_";
       next;
    }

    chomp;
    s/\n/ /g;


    #Lowercase 
    #$_ = lc($_);
    #s/Å/å/g;
    #s/Ä/ä/g;
    #s/Ö/ö/g;

    #Strange chars
    s/À/a/g;
    s/Á/a/g;
    s/Â/a/g;
    s/Ã/a/g;
    s/Æ/a/g;
    s/Ç/c/g;
    s/È/e/g;
    s/É/e/g;
    s/Ê/e/g;
    s/Ë/e/g;
    s/Ì/i/g;
    s/Í/i/g;
    s/Î/i/g;
    s/Ï/i/g;
    s/Ð/d/g;
    s/Ñ/n/g;
    s/Ò/o/g;
    s/Ó/o/g;
    s/Ô/o/g;
    s/Õ/o/g;
    s/Ø/ö/g;
    s/Ù/u/g;
    s/Ú/u/g;
    s/Û/u/g;
    s/Ü/u/g;  
    s/Ý/y/g;
    s/Þ/p/g;
    s/ß/b/g;
    s/á/a/g;
    s/à/a/g;
    s/â/a/g;
    s/ã/a/g;
    s/æ/ä/g;
    s/ç/c/g;
    s/è/e/g;
    s/ê/e/g;
    s/ë/e/g;
    s/é/e/g;
    s/ð/d/g;
    s/ì/i/g;
    s/í/i/g;
    s/î/i/g;
    s/ï/i/g;
    s/ò/o/g;
    s/ó/o/g;
    s/ô/o/g;
    s/õ/o/g;
    s/ñ/n/g;
    s/ø/ö/g;
    s/¨/s/g;
    s/ü/u/g;
    s/ù/u/g;
    s/ú/u/g;
    s/û/u/g;
    s/µ/u/g;
    s/ý/y/g;
    s/þ/t/g;
    s/ÿ/y/g;
    s/´/z/g;
    s/¸/z/g;
    s/¦/s/g;
    s/Ü/u/g;

    #Remove annotations 
    s!\/\S*\/!!g;
    s!\S+\/!!g; 
    s!\/\S+!!g; 
   
    #Try to remove white space and blank lines
    s/^*\n//;
    s/^\s+//;
    s/\s+$//;
    s/^\n//;
    next if (/^\s*$/);

    # Remove comments
    s!\s*///*.*?///*\s*! !g;

    # Remove place-date-source lines.
    next if (/^\S.*, \d+\.\s*\d+\.\s*\(.*\)\s*$/);

    # Try to remove signatures
    next if (length($_) < 1); # short lines are usually signatures

    # Connect numbers and convert commas
    s!(\d) (\d)!$1$2!g;
    s!(\d)\s*,\s*(\d)!$1 pilkku $2!g;

    # Remove "ajatusviiva" 
    s!\s+-\s+! !g;

    # Remove some special characters
    s![-\"']! !g;
    s!\.\.\.!. !g;
    s!eu\s*:n!eun!g;


    # Remove urls:
    s!http\S+! !g;

    # Remove parentheses
    s!\s*\(.*?\)\s*! !g;
    s!\s*\.*?\)\s*! !g; 
    s!\s*\(.*?\s*! !g;    
    s!\s*\[.*?\]\s*! !g;
    s!\s*\.*?\]\s*! !g; 
    s!\s*\[.*?\s*! !g;
    
    # Some abbreviations
    s!\bjr.!junior !gi;
    s!\binc.!inc !gi;
    s!(\d+)\s*m/s!$1 metriä sekunnissa!g;
    s!(\d+)\s*r/min!$1 kierrosta minuutissa!g;
    s!(\d+)\s+kpm\b!$1 kilopondimetriä!g;
    s!(\d+)\s+kW/l\b!$1 kilowattia litraa kohti!g;
    s!(\d+)\s+kW\b!$1 kilowattia!g;
    s!(\d+)\s+hv/l\b!$1 hevosvoimaa litraa kohti!g;
    s/1½/ yksi ja puoli /g;
    s/½/ puoli /g;
    s/m²:n/neliömetrin/g;
    s/\/\s*m²/ per neliömetri/g;
    s/\S*[²³]\S*//g;
    s/±/plus miinus /g;
    s/(\d+)\s*°C/$1 Celcius astetta/g;
    s/(\d+)\s*°/$1 astetta/g;
    s/(klo|kello)\s+(\d+)\.(\d+)/kello $2\#NOM $3\#NOM/g;
    s/£/puntaa/g;
    s/\$/dollaria/g;
    s/¤/euroa/g;
    s/\%/prosenttia/g;
    s/\besim\./esimerkiksi /gi;
    s/\bpat\. no\.?/patentti numero /gi;
    s/\bo\.s\./omaa sukua /gi;
    #s/\bn\./noin/g;
    s/\bts\./tai siis /g;
    s/\bev\. ?lut\./evankelisluterilainen /g;
    s/\bpros\./prosenttia/g;
    s/\bk\.?o\./kyseessä oleva /gi;
    s/\bjne./ja niin edelleen /gi;
    s/\bem\./edellä mainittu /g;
    s/\bent\./entinen /gi;
    s/\bop\.\s*(\d+)/opus $1 /gi;
    s/\bkv\./kansainvälinen /gi;
    s/\bns\./niin sanottu /gi;
    s/\bnk\./niin kutsuttu /g;
    s/\bvt\./virkaatekevä /g;
    s/\bp\.\s+(\d+)/puhelin $1/g;
    s/\bpuh\.\s+(\d+)/puhelin $1/g;
    s/\bv\.\s+(\d+)/vuonna $1/g;
    s/\b(s|synt)\.\s*(19\d\d)/syntynyt $1/g;
    s/\bym\./ynnä muuta /gi;
    s/\byms\./ynnä muuta sellaista /gi;
    s/\boy\./osakeyhtiö /gi;
    s/\bry\./rekisteröity yhdistys /gi;
    s/\bmm\./muun muassa /gi;
    s/\bmrd\. mk\./miljardia markkaa /g;
    s/\bmrd\./miljardia /g;
    s/\bmilj\./miljoonaa /g;
    s!\bvas\.!vasemmistoliitto !gi;
    s!\bvihr\.!vihreä liitto !gi;
    s!\bV65\b!vee kuusi viisi !g;
    s!\be. ?Kr.!ennen kristusta !g;
    s!\beKr\.?!ennen kristusta !g;
    s!\bks\. ?ed.!kansanedustaja !g;
    s!\bpj\. ?ed.!puheenjohtaja !g;
    s!\b[Tt]oim\. ?joht.!toimitusjohtaja !g;
    s!\b[Oo]pett\. ?!opettaja !g;
    s!\b[Pp]uh\. ?joht.!puheenjohtaja !g;
    s!\b[Kk]auppat\.!kauppatieteiden !g;
    s!\b[Kk]asvatustiet\.!kasvatustieteiden !g;
    s!\b[Vv]altiotiet\.!valtiotieteiden !g;
    s!\b[Ll]ääket\.!lääketieteen !g;
    s!\b[Mm]aist\.!maisteri !g;
    s!\b[Ll]is\.!lisensiaatti !g;
    s/(\d+)\s+hv\b/$1 hevosvoimaa/g;
    s/(\d+)\s+g\b/$1 grammaa/g;
    s/(\d+)\s+mg\b/$1 milligrammaa/g;
    s/(\d+)\s+dl\b/$1 desilitraa/g;
    s/(\d+)\s+l\b/$1 litraa/g;
    s/(\d+)\s+bar\b/$1 baaria/g;
    s/(\d+)\s+kg\b/$1 kilogrammaa/g;
    s/(\d+)\s+km\b/$1 kilometriä/g;
    s/(\d+)\s+kk\b/$1 kuukautta/g;
    s/(\d+)\s+mm\b/$1 millimetriä/g;
    s/(\d+)\s+cm\b/$1 senttimetriä/g;
    s/(\d+)\s+min\b/$1 minuuttia/g;
    s/(\d+)\s+m\b/$1 metriä/g;
    s/(\d+)\s+h\b/$1 tuntia/g;
    s/(\d+)\s+mk\b/$1 markkaa/g;
    s/(\d+)\s*v\b/$1 vuotta/g;
    s/\.000(?=\D)/000/g;
    s/(\d+)\s*(\.)?\s*-\s*(\d+)/$1$2 viiva $3/g;
    s/(\d+)\s*\.\s*(\d+)\s*\./ $1\#JNOM $2\#JPAR /g;
    s/(\d+)\.(\d+)/$1 piste $2/g;
    s/(\d+),(\d+)/$1 pilkku $2/g;
    s/\+/ plus /g;


    ##################################################
    # Inflect numbers
    ##################################################
    # Nollalla alkavat numerot erikseen
    s/(?<![0-9])(0\d*)(\#[A-Z\#]+)?/$1\#ERI/g;

    # 5:n -> viiden
    s/(\d+):n/$1\#GEN/g;

    # 5:stä -> viidestä
    s/(\d+):st[aä]/$1\#ELA/g;

    # 5 kilometrin -> viiden
    s/(\d+)(\s+\S+in)\b/$1\#GEN $2/g;

    # 7:ää -> seitsemää
    s/(\d+):ää/$1\#PAR/g;
    s/(\d+):aa/$1\#PAR/g;
    s/(\d+):t?tä/$1\#PAR/g;
    s/(\d+):t?ta/$1\#PAR/g;

    # 5:een -> viiteen
    s/(\d+):een/$1\#ILL/g;

    # 5:llä -> viidellä
    s/(\d+):ll[aä]/$1\#ADE/g;

    # 12. [a-z] -> kahdestoista
    s/(\d+)\.\s+([a-zäöå])/$1\#JNOM $2/g;

    # 1900 luvulla -> tuhatyhdeksänsataa (estää ADESSIIVIN myöhemmin)
    s/(\d+)\s*(luvulla)/$1\#NOM $2/g;

    # 11 . syyskuuta -> yhdestoista
    s/(\d+)\s*\.\s*(tammi|helmiexclude strange characters|maalis|huhti|touko|kesä|heinä|elo|syys|loka|marras|joulu)/$1\#JNOM $2/gi;

    # 100 foobariksi -> sadaksi
    s/(\d+)\s+(\w+ksi)/$1\#TRA $2/gi;

    # 5 foobarilla -> viidellä
    s/(\d+)\s+(\w+ll[aä])/$1\#ADE $2/gi;

    # 6 foobarissa -> kuudessa
    s/(\d+)\s+(\w+ss[aä])/$1\#INE $2/gi;

    # 10 foobariin -> kymmeneen
    s/(\d+)\s+(?=\w+(een|iin|ään|aan))/$1\#ILL /gi;

    # Convert numbers into written form
    s/\d+(\#[A-Z]+)?/Numbers_FI::convert($&)/ge;

    ##################################################

    # Remove commas, colons, semicolons, and other weird characters 
    s!,! !g;
    s!:!!g;
    s!: ! !g;
    s!:\s*$!!g;
    s!(\S):(\S)!$1$2!g;
    s!;! !g;
    s!/! !g;
    s!§! !g;
    s!_! !g;
    s!ß! !g;
    s!\^! !g;
    s!\*! !g; 
    s!»! !g;
    s!«! !g;
    s!&! !g;
    s!º!!g;
    s!¡!!g;
    s!©!!g;
    s!ª!!g;
    s!¬!!g;
    s!®!!g;
    s!¯!!g;
    s!±!!g;
    s!²!!g;
    s!³!!g;
    s!¶!!g;
    s!·!!g;
    s!¹!!g;
    s!º!!g;
    s!¿!!g;
    s!×!!g;
    s!÷!!g;
    s!¼!!g;
    s!~!!g;
    s!@!!g;
    s!#!!g;
    s!|!!g;
    s!\(!!g;
    s!\)!!g;
    s!\{!!g;
    s!\}!!g;

    #Remove still remaining non-alphabetic charcters
    s/[^abcdefghijklmnopqrstuvwxyzåäöABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ.!?0123456789]/ /g;
    #Remove empty lines
    s/^*\n//;
    s/^\s+//;
    s/\s+$//;
    s/  / /g;

    # One sentence per line
    @snt = split(/\s*[.!?]\s*/);
    $arraySize = @snt;
    $arraySize = scalar (@snt);
    $arraySize = $#snt + 1;
    foreach my $val (@snt) 
    {
        print "$val\n";
        #print "$val ";
    }
}
