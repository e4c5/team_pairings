select * from tournament_tournament tt where name like '%Junior%'


select tp.name, ae.e  from profiles_profile pp 
	inner join auth_user au on 
		au.id = pp.user_id 
	inner join tournament_participant tp on
		au.id  = tp.user_id
	inner join account_emailaddress ae on
		ae.user_id = au.id 
	inner join tournament_tournament tt on
		tt.id = tp.tournament_id 
	where ae.verified = true
	order by tp.name;
	

select tt.name, count(*) from tournament_tournament tt 
	inner join tournament_participant tp  on tt.id = tp.tournament_id 
	where tt.name like '%Junior%'
	group by tt.name;