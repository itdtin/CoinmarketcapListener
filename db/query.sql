select cmc_id, min_max_date_rank_diff from(
select cmc_id, last_update as created_date, rank as value,
(first_value(rank) over(partition by cmc_id order by last_update asc) - first_value(rank) over(partition by cmc_id order by last_update desc)) as min_max_date_rank_diff,
row_number() over(PARTITION by cmc_id order by last_update) num,
rank() over(partition by cmc_id order by rank) rank_rank,
DENSE_RANK () over(partition by cmc_id order by rank) dense_rank_rank
from rank_historical rh
where last_update between "2021-08-24" and "2021-08-29")
group by cmc_id order by min_max_date_rank_diff desc
