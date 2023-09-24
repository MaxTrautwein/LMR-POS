# LMR-POS
POS System developed for use in the LMR

## Save to SQL
see https://stackoverflow.com/a/29913462

```
docker exec -t <ID> pg_dumpall -c -U lmr > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```
