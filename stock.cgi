#!/usr/bin/env perl
# stock.cgi
# hogefoobar*

use strict;
use warnings;
use utf8;
use Coro;
use Coro::LWP;
use URI;
use CGI;
use Web::Scraper;

my $q					= CGI->new();
my @list				= split (/,/, $q->param('q'));
my $display_snum		= 1 if $q->param('display_snum') eq 1;
my $remove_kabu_true	= 1 if $q->param('kabu') eq 1;
my $remove_comma_true	= 1 if $q->param('comma') eq 1;


# print useage if no param provided
&usage unless @list;


# start html
print $q->header . $q->start_html;

# main
my @coros;

for my $stock_num (@list) {
	push @coros, async {
		my ($name,$price) = &get_stock_of( $stock_num );
		$name	= $name . '(' . $stock_num . ')'	if $display_snum;
		$name	= &remove_kabu($name)				if $remove_kabu_true;
		$price	= &remove_comma($price)				if $remove_comma_true;
		printf "%s:%s", $name, $price;
		print $q->br, "\n";
	};
}
$_->join for @coros;


# end html
print $q->end_html;


# subs
sub get_stock_of {
	my $stock_num	= shift;
	my $yahoo_stock	= URI->new(qq{http://stocks.finance.yahoo.co.jp/stocks/detail/?code=$stock_num});
	my $scraper		= scraper {
			process 'h1', 'name[]' => 'TEXT';
			process 'td.stoksPrice', 'price[]' => 'TEXT';
			};
	my $result		= $scraper->scrape($yahoo_stock);
	return $result->{'name'}[0], $result->{'price'}[1];
}

sub remove_kabu {
	my $str		= shift;
	my $kabu	= q/\(株\)/;
	$str =~ s/$kabu//;
	return $str;
}

sub remove_comma {
	my $str		= shift;
	my $comma	= q/,/;
	$str =~ s/$comma//g;
	return $str;
}


sub usage {
	print "NO QUERY PROVIDED!! <br />";
	print "USAGE:<br />";
	print qq|
		<a href="http://$ENV{'HTTP_HOST'}/stock.cgi?q=2491.T,9501,3765.Q,9984.T">
		http://$ENV{'HTTP_HOST'}/stock.cgi?q=2491.T,9501,3765.Q,9984.T
		</a>
		|;
	print $q->br;
	print qq|
		<a href="http://$ENV{'HTTP_HOST'}/stock.cgi?q=2491.T,9501,3765.Q,9984.T&kabu=1&comma=1&display_snum=1">
		http://$ENV{'HTTP_HOST'}/stock.cgi?q=2491.T,9501,3765.Q,9984.T&kabu=1&comma=1&display_snum=1
		</a>
		|;

	exit 0;
}
__END__
