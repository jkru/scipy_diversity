ODIR = ../../data/scs_outputs

stats : outputs
	rm -f ${ODIR}/scipy_stats
	egrep -h '^##' ${ODIR}/o????.dat > ${ODIR}/scipy.stats

outputs: scipy_conf_stats.py name_class.py scipy_conf_parsers.py
	mkdir -p ${ODIR}/
	./scipy_conf_stats.py 2002 > ${ODIR}/o2002.dat
	./scipy_conf_stats.py 2003 > ${ODIR}/o2003.dat
	./scipy_conf_stats.py 2004 > ${ODIR}/o2004.dat
	./scipy_conf_stats.py 2005 > ${ODIR}/o2005.dat
	./scipy_conf_stats.py 2006 > ${ODIR}/o2006.dat
	./scipy_conf_stats.py 2007 > ${ODIR}/o2007.dat
	./scipy_conf_stats.py 2008 > ${ODIR}/o2008.dat
	./scipy_conf_stats.py 2009 > ${ODIR}/o2009.dat
	./scipy_conf_stats.py 2010 > ${ODIR}/o2010.dat
	./scipy_conf_stats.py 2011 > ${ODIR}/o2011.dat
	./scipy_conf_stats.py 2012 > ${ODIR}/o2012.dat
	./scipy_conf_stats.py 2013 > ${ODIR}/o2013.dat
	./scipy_conf_stats.py 2014 > ${ODIR}/o2014.dat
	./scipy_conf_stats.py 2015 > ${ODIR}/o2015.dat
	./scipy_conf_stats.py 2016 > ${ODIR}/o2016.dat
	./scipy_conf_stats.py 2017 > ${ODIR}/o2017.dat

