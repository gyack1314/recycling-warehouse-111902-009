"""生成未排序、多分片的仓库输入，不生成导出结果。"""
import argparse,json,hashlib
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
def generate(out,rows):
    if rows<1:raise ValueError("rows须为正整数")
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    names=[]
    for shard in range(4):
        path=out/("part-"+str(shard)+".parquet");names.append(path.name)
        schema=pa.schema([("day",pa.string()),("site",pa.string()),("weight",pa.string()),("sort_value",pa.int64()),("note",pa.string())])
        with pq.ParquetWriter(path,schema,compression="zstd") as writer:
            buffer=[]
            for i in range(shard,rows,4):
                buffer.append({"day":"2026-10-"+str(1+i%3).zfill(2),"site":"N" if i%2 else "S","weight":str(i%17)+".000","sort_value":None if i%7==0 else i%5,"note":"合成"})
                if len(buffer)==1024:writer.write_table(pa.Table.from_pylist(buffer,schema=schema));buffer=[]
            if buffer:writer.write_table(pa.Table.from_pylist(buffer,schema=schema))
    (out/"versions.json").write_text(json.dumps({"S-large":names},indent=2),encoding="utf-8")
    (out/"generation.json").write_text(json.dumps({"rows":rows,"shards":4},indent=2),encoding="utf-8")
    return names
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);p.add_argument("--rows",type=int,default=200000)
    a=p.parse_args();print(json.dumps(generate(a.out,a.rows)))
