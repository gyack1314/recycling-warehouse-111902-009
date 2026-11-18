import json,unittest,tempfile,shutil
from decimal import Decimal
from pathlib import Path
import pyarrow.parquet as pq
from materials.physical import load_inventory
ROOT=Path(__file__).resolve().parents[1]

class InputMaterials(unittest.TestCase):
    def test_real_files_and_independent_values(self):
        records=load_inventory(ROOT/"inputs")
        self.assertTrue(records)
        seed=json.loads((ROOT/"inputs/seed.json").read_text(encoding="utf-8"))
        for name,rows in seed.items():
            self.assertEqual(pq.read_table(ROOT/"inputs"/(name+".parquet")).to_pylist(),rows)

    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/"inputs";shutil.copytree(ROOT/"inputs",target)
            inv=json.loads((target/"inventory.json").read_text(encoding="utf-8"))
            p=target/inv["files"][0]["path"];p.write_bytes(p.read_bytes()+b"x")
            with self.assertRaisesRegex(ValueError,"摘要"):load_inventory(target)

    def test_business_material_shapes(self):
        seed=json.loads((ROOT/"inputs/seed.json").read_text(encoding="utf-8"))
        actions=json.loads((ROOT/"inputs/actions.json").read_text(encoding="utf-8"))
        self.assertEqual(seed['part_a'][0],seed['part_a'][1])
        self.assertIsNone(seed['part_a'][2]['sort_value'])
        self.assertNotIn('sort_value',seed['requests'][0]['columns'])
        versions=json.loads((ROOT/'inputs/versions.json').read_text(encoding='utf-8'))
        self.assertNotEqual(versions['S1'],versions['S2'])

    def test_streaming_input_generation(self):
        from materials.generate import generate
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)/"raw"
            files=generate(destination,207)
            self.assertEqual(sum(pq.ParquetFile(destination/x).metadata.num_rows for x in files),207)
            self.assertEqual(len(files),4)
