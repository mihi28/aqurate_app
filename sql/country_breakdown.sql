create or replace view country_breakdown as
select orders.country, round(sum(
                                case
                                when orders.currency = 'EUR' then orders.unit_price * orders.qty
                                else (orders.unit_price * orders.qty) / exchange.rate
                                end
                              )::numeric,2)::float
          as total_spent
  from clean_orders orders
left join lateral(
        select fx.rate
        from exchange_rates fx
        where orders.currency = fx.quote
              and orders.fx_reference_date >= fx.date
        order by fx.date desc
        limit 1
      ) exchange on orders.currency != 'EUR'
  where orders.category = 'Books' or orders.category = 'Electronics'
group by country
having round(sum(
                  case
                  when orders.currency = 'EUR' then orders.unit_price * orders.qty
                  else (orders.unit_price * orders.qty) / exchange.rate
                  end
                )::numeric,2)::float > 40000
order by total_spent desc;