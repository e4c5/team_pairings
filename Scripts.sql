select * from tournament_tournament tt where name like '%Junior%'


select tp.name, ae.email , approval, payment from profiles_profile pp 
	inner join auth_user au on 
		au.id = pp.user_id 
	inner join tournament_participant tp on
		au.id  = tp.user_id
	inner join account_emailaddress ae on
		ae.user_id = au.id 
	inner join tournament_tournament tt on
		tt.id = tp.tournament_id 
	--where approval='P' and payment=''
		where tournament_id = 47 or tournament_id = 54
	order by tp.name;
	

select tt.name, count(*) from tournament_tournament tt 
	inner join tournament_participant tp  on tt.id = tp.tournament_id 
	where tt.name like '%Junior%'
	group by tt.name;
	
update tournament_participant set game_wins = 0 where game_wins is null

select * from tournament_participant tp


delete from tournament_participant where approval = 'V' and tournament_id = 47


select * from profiles_profile pp 