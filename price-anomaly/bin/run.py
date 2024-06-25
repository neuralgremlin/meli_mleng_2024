#!/usr/bin/env python

from price_anomaly import Config, DatasetBuilder, seed_everything, ModelBuilder

seed_everything()


def main():
    print("Iniciando Ejecución")
    data_path = Config.Path.DATA_DIR / "raw" / "precios_historicos.csv"
    clean_path = Config.Path.DATA_DIR / "clean" / "processed_data.csv"
    print("Preparando Dataset")
    DatasetBuilder().build(data_path, clean_path)
    print("Entrenando Modelo")
    ModelBuilder().run(clean_path, Config.Path.MODELS_DIR)


if __name__ == "__main__":
    main()
