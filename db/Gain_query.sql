
select cmc_id, c.ticker, update_date, a.first_value, a.last_value, gain from (
select rh.cmc_id as cmc_id, rh.last_update as update_date,
(first_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) - last_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update)) as gain,
first_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) first_value,
last_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) last_value,
row_number() over(partition by rh.cmc_id order by rh.last_update desc) seq
from rank_historical rh  where rh.last_update between '2021-08-24' and '2021-08-31') a left join currencies c on a.cmc_id=c.id where seq = 1 and gain != 0 order by gain desc limit 100



amdn aksndaljkslklkamsdlak
sadaksjndkasjndln
