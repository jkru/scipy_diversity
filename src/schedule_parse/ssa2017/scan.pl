#!/usr/bin/perl -w

my @files = <yob*.txt>;

my %both = ();
my %data = ();

foreach my $f (@files) {
    my $year = $f;
    $year =~ s/yob(\d+).txt/$1/;
    open(I,$f);
    while(<I>) {
	chomp;
	($name,$gender,$count) = split /,/;
	$name = lc($name);

	$data{$name}{$gender}{$year} = $count;
	
	$opposite = $gender;
	$opposite =~ y/FM/MF/;

	if (exists($data{$name}{$opposite})) {
	    push @{ $both{$name} }, $year;
	}
    }
    close(I);
}

foreach $key (keys(%both)) {
    my $years = join ' ', @{ $both{$key} };
    print "$key $years\n";
}
	
	
	   
