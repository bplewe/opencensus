update households h set pt_type = 'interpolated',
addresspt = (select case 
  when mod(cast(replace(replace(house_number,'*',''),'?','') as integer), 2.0) = mod(s2.froml1900, 2.0)
    then (st_lineinterpolatepoint(st_offsetcurve(s2.geom,20),
								  abs(cast(replace(replace(h.house_number,'*',''),'?','') as real) - s2.froml1900)/
								  (0.1+ abs(s2.tol1900 - s2.froml1900))))
  when mod(cast(replace(replace(house_number,'*',''),'?','') as integer), 2.0) = mod(s2.fromr1900, 2.0)
    then (st_lineinterpolatepoint(st_offsetcurve(s2.geom,-20),
								  1.0-(abs(cast(replace(replace(h.house_number,'*',''),'?','') as real) - s2.fromr1900)/
								  (0.1+ abs(s2.tor1900 - s2.fromr1900)))))
  end as addresspt
 from streets s2
 where (trim(replace(replace(h.dir || ' ' || h.street,'*',''),'?','')) in (s2.dirname1898,  s2.diralias1898))
 and ((cast(replace(replace(h.house_number,'*',''),'?','') as integer) between least(s2.froml1900,s2.tol1900) and greatest(s2.froml1900,s2.tol1900))
 or (cast(replace(replace(h.house_number,'*',''),'?','') as integer) between least(s2.fromr1900,s2.tor1900) and greatest(s2.fromr1900,s2.tor1900)))
	limit 1) 
where (pt_type = 'interpolated' or pt_type is null) and h.street > '* ' and h.house_number ~ '^\*?[0-9]+\??$';

update households set pt_type = null where addresspt is null and pt_type = 'interpolated'; 