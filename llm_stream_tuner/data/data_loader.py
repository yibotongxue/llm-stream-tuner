import builtins
import random
from typing import Any

from ..utils.type_utils import AlpacaInputData
from .data_formatter import DataFormatterRegistry


class TrainDataLoader:
    def __init__(self, data_cfgs: dict[str, Any]):
        self.data_cfgs = data_cfgs

    def load_dataset(self) -> list[AlpacaInputData]:
        template: str = self.data_cfgs["data_template"]
        data_formatter = DataFormatterRegistry.get_by_name(template)()

        # 数据大小
        data_size = self.data_cfgs.get("data_size")

        # 加载数据
        load_type = self.data_cfgs.get("load_type", "datasets")
        if load_type == "datasets":
            from datasets import load_dataset

            data_path = self.data_cfgs["data_path"]
            load_cfgs = self.data_cfgs.get("load_cfgs", {})
            dataset = load_dataset(path=data_path, **load_cfgs)
        elif load_type == "modelscope":
            from modelscope.msdatasets import MsDataset

            data_path = self.data_cfgs["data_path"]
            load_cfgs = self.data_cfgs.get("load_cfgs", {})
            dataset = MsDataset.load(data_path, **load_cfgs)
        elif load_type == "pandas":
            from datasets import Dataset
            from pandas import read_csv

            data_files = self.data_cfgs["data_files"]
            read_csv_args = self.data_cfgs.get("read_csv_args", {}).copy()
            if "dtype" in read_csv_args:
                read_csv_args["dtype"] = getattr(builtins, read_csv_args["dtype"])
            df = read_csv(
                data_files,
                **read_csv_args,
            )
            dataset = Dataset.from_pandas(df)
        raw_samples = [
            data_formatter.format_conversation(raw_sample) for raw_sample in dataset
        ]

        shuffle_seed = self.data_cfgs.get("shuffle_seed", 46)
        random.seed(shuffle_seed)
        random.shuffle(raw_samples)

        if data_size is not None:
            raw_samples = raw_samples[: min(data_size, len(raw_samples))]
        return raw_samples


def main() -> None:
    import argparse

    from ..utils.config import (
        deepcopy_config,
        load_config,
        update_config_with_unparsed_args,
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config-file-path",
        type=str,
        default="./configs/star1_data.yaml",
        help="The path to the config file",
    )
    args, unparsed_args = parser.parse_known_args()

    cfgs = load_config(args.config_file_path)
    update_config_with_unparsed_args(unparsed_args=unparsed_args, cfgs=cfgs)

    cfgs = deepcopy_config(cfgs)

    data_loader = TrainDataLoader(cfgs)
    dataset = data_loader.load_dataset()
    print(dataset[0])


if __name__ == "__main__":
    main()
