# Dataset Schema Report

## Executive Summary

- Total files audited under `datasets/`: 75
- Files with direct label candidates: 31
- Final supervised baseline uses a single-source dataset because no trustworthy row-level merge exists across the discovered sources.
- Supporting Indonesia-first soil and climate sources are retained for future geospatial enrichment, not for the current supervised baseline.

## Final Dataset Decision

- Selected primary dataset: `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- Reason: strongest direct linkage between soil chemistry, weather variables, and crop labels; complete rows; no duplicates; no missing values before hard-domain validation.
- Explicitly rejected for baseline merge: benchmark mirror dataset, synthetic CTGAN dataset, Indonesia soil-only profiles, climate rasters, and rule-base resources.

## Primary Training Candidate

| relative_path | rows | columns_count | target_candidate | merge_feasibility | notes |
| --- | --- | --- | --- | --- | --- |
| datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv | 3867 | 29 | label | single_source_selected | 3867 rows. Best directly supervised dataset among downloaded files because it links soil nutrients and multiple weather features to crop labels. The downloadable CSV does not actually expose latitude/longitude despite the dataset description claiming coordinates. Best directly supervised crop-label dataset. |
| datasets/raw/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv | 3867 | 29 | label | single_source_selected | 3867 rows. Best directly supervised dataset among downloaded files because it links soil nutrients and multiple weather features to crop labels. The downloadable CSV does not actually expose latitude/longitude despite the dataset description claiming coordinates. Best directly supervised crop-label dataset. |

## Other Relevant Files

| relative_path | recommended_role | rows | columns_count | target_candidate | merge_feasibility |
| --- | --- | --- | --- | --- | --- |
| datasets/csv/mendeley_v9r8c2cyp2_soil_physical_chemical_properties.csv | alternative_vegetation_label_dataset | 108 | 15 | Vegetation types | label_space_incompatible |
| datasets/raw/mendeley_v9r8c2cyp2_soil_physical_chemical_properties.xlsx | alternative_vegetation_label_dataset | 108 | 15 | Vegetation types | label_space_incompatible |
| datasets/csv/github_nileshiq_crop_recommendation.csv | benchmark_training_candidate | 2200 | 8 | Crop | append_only_possible_but_rejected |
| datasets/raw/github_nileshiq_crop_recommendation.csv | benchmark_training_candidate | 2200 | 8 | Crop | append_only_possible_but_rejected |
| datasets/csv/github_openclim_ecocrop_db_secondtrim.csv | rule_base_support | 634 | 32 |  | label_level_only |
| datasets/csv/github_openclim_ecocrop_variable_lookup.csv | rule_base_support | 53 | 2 |  | label_level_only |
| datasets/raw/github_openclim_ecocrop_db_secondtrim.csv | rule_base_support | 634 | 32 |  | label_level_only |
| datasets/raw/github_openclim_ecocrop_variable_lookup.csv | rule_base_support | 53 | 2 |  | label_level_only |
| datasets/csv/mendeley_nv7jbmkynm_indonesia_pdsi_grid_1980_2019.csv | supporting_climate_or_raster | 19255 | 10 |  | requires_geospatial_join |
| datasets/csv/mendeley_nv7jbmkynm_indonesia_pdsi_temporal_1980_2019.csv | supporting_climate_or_raster | 480 | 5 |  | requires_geospatial_join |
| datasets/raw/mendeley_nv7jbmkynm_indonesia_pdsi_grid_1980_2019.csv | supporting_climate_or_raster | 19255 | 10 |  | requires_geospatial_join |
| datasets/raw/mendeley_nv7jbmkynm_indonesia_pdsi_temporal_1980_2019.csv | supporting_climate_or_raster | 480 | 5 |  | requires_geospatial_join |
| datasets/raw/worldclim_wc2.1_10m_prec.zip | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/worldclim_wc2.1_10m_tavg.zip | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/zenodo_17496280_esa_soil_moisture_01.tif | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/zenodo_17496280_esa_soil_moisture_02.tif | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/zenodo_17496280_esa_soil_moisture_03.tif | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/zenodo_17496280_esa_soil_moisture_04.tif | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/zenodo_17496280_esa_soil_moisture_05.tif | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/raw/zenodo_17496280_esa_soil_moisture_06.tif | supporting_climate_or_raster | 0 | 0 |  | requires_geospatial_join |
| datasets/csv/isric_wosis_latest_cecph7_indonesia.csv | supporting_soil_backbone | 924 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_clay_indonesia.csv | supporting_soil_backbone | 889 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_elco25_indonesia.csv | supporting_soil_backbone | 243 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_nitkjd_indonesia.csv | supporting_soil_backbone | 799 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_orgc_indonesia.csv | supporting_soil_backbone | 1285 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_phaq_indonesia.csv | supporting_soil_backbone | 953 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_phetb1_indonesia.csv | supporting_soil_backbone | 5 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_phetol_indonesia.csv | supporting_soil_backbone | 21 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_sand_indonesia.csv | supporting_soil_backbone | 883 | 19 |  | no_direct_label_key |
| datasets/csv/isric_wosis_latest_silt_indonesia.csv | supporting_soil_backbone | 883 | 19 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_cecph7_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_clay_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_elco25_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_nitkjd_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_orgc_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_phaq_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_phetb1_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_phetol_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_sand_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/raw/isric_wosis_latest_silt_indonesia.geojson | supporting_soil_backbone | 0 | 0 |  | no_direct_label_key |
| datasets/csv/zenodo_17666722_barley_training_samples.csv | supporting_spatial_label_dataset | 64000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_cassava_training_samples.csv | supporting_spatial_label_dataset | 10000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_cotton_training_samples.csv | supporting_spatial_label_dataset | 10000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_gaez_glues_classified_area_comparison.csv | supporting_spatial_label_dataset | 17 | 3 | crop | requires_spatial_join |
| datasets/csv/zenodo_17666722_gaez_glues_suitability_index_comparison.csv | supporting_spatial_label_dataset | 17 | 4 | Crop | requires_spatial_join |
| datasets/csv/zenodo_17666722_gaez_thisstudy_classified_area_comparison.csv | supporting_spatial_label_dataset | 18 | 3 | crop | requires_spatial_join |
| datasets/csv/zenodo_17666722_gaez_thisstudy_suitability_index_comparison.csv | supporting_spatial_label_dataset | 18 | 4 | Crop | requires_spatial_join |
| datasets/csv/zenodo_17666722_maize_training_samples.csv | supporting_spatial_label_dataset | 50000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_millet_training_samples.csv | supporting_spatial_label_dataset | 10000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_oilpalm_training_samples.csv | supporting_spatial_label_dataset | 40000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_paddy_rice_training_samples.csv | supporting_spatial_label_dataset | 8158 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_peanut_training_samples.csv | supporting_spatial_label_dataset | 10000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_potato_training_samples.csv | supporting_spatial_label_dataset | 16000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_rapeseed_training_samples.csv | supporting_spatial_label_dataset | 40000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_rye_training_samples.csv | supporting_spatial_label_dataset | 16000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_sorghum_training_samples.csv | supporting_spatial_label_dataset | 16000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_soybean_training_samples.csv | supporting_spatial_label_dataset | 24000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_sugarbeet_training_samples.csv | supporting_spatial_label_dataset | 64000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_sugarcane_training_samples.csv | supporting_spatial_label_dataset | 10000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_sunflower_training_samples.csv | supporting_spatial_label_dataset | 56000 | 4 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_training_samples_combined.csv | supporting_spatial_label_dataset | 564158 | 5 | label | requires_spatial_join |
| datasets/csv/zenodo_17666722_wheat_training_samples.csv | supporting_spatial_label_dataset | 120000 | 4 | label | requires_spatial_join |
| datasets/raw/zenodo_17666722_training_samples_for_17_crops.zip | supporting_spatial_label_dataset | 0 | 0 |  | requires_spatial_join |
| datasets/csv/mendeley_vynxnppr7j_crop_recommendation.csv | synthetic_training_candidate | 57000 | 23 | CROPS | append_only_possible_but_rejected |
| datasets/raw/mendeley_vynxnppr7j_crop_recommendation.csv | synthetic_training_candidate | 57000 | 23 | CROPS | append_only_possible_but_rejected |

## Merge Assessment

- `ds003` + `ds001`: only safe as benchmark comparison, not as a single training table, because feature semantics and crop label spaces differ.
- `ds003` + `ds002`: possible append-only experiment, but rejected for default because `ds002` includes synthetic CTGAN-expanded records.
- `ds003` + Indonesia soil/climate sources: not feasible for row-level merge because the supervised crop dataset lacks lat/lon keys in the downloadable table.
- WoSIS + WorldClim + ESA Soil Moisture + GAEZ/Zenodo remains a valid future Indonesia-first geospatial modeling pipeline, but it requires spatial extraction and weak-label design beyond the current baseline.

## Final Dataset Schemas

### `final_dataset.csv`

| Column | Description |
| --- | --- |
| `record_id` | Stable row identifier generated during preparation. |
| `source_dataset` | Provenance marker for the selected training source. |
| `soil_color` | Normalized soil color category derived from the raw soil color text. |
| `ph` | Soil pH from the source dataset. |
| `nitrogen` | Soil nitrogen measurement from the source dataset. |
| `phosphorus` | Soil phosphorus measurement from the source dataset. |
| `potassium` | Soil potassium measurement from the source dataset. |
| `zinc` | Soil zinc measurement from the source dataset. |
| `sulfur` | Soil sulfur measurement from the source dataset. |
| `specific_humidity_mean` | Mean seasonal specific humidity computed from the four QV2M features. |
| `temperature_mean` | Average seasonal mean temperature computed from max/min seasonal values. |
| `temperature_seasonal_range` | Maximum seasonal temperature minus minimum seasonal temperature. |
| `rainfall_mean` | Mean seasonal corrected precipitation across the four source precipitation columns. |
| `rainfall_total_proxy` | Sum of the four seasonal precipitation columns retained as a total-rainfall proxy. |
| `soil_moisture_surface` | Top-layer soil moisture proxy from the source dataset. |
| `cloud_amount` | Cloud amount feature from the source dataset. |
| `surface_pressure` | Surface pressure feature from the source dataset. |
| `target_crop` | Normalized crop label used as the supervised learning target. |

### `final_dataset_minimal.csv`

- Columns: record_id, source_dataset, soil_color, ph, nitrogen, phosphorus, potassium, temperature_mean, rainfall_mean, soil_moisture_surface, target_crop

### `final_dataset_extended.csv`

- Columns: record_id, source_dataset, soil_color, ph, nitrogen, phosphorus, potassium, zinc, sulfur, specific_humidity_winter, specific_humidity_spring, specific_humidity_summer, specific_humidity_autumn, temperature_max_winter, temperature_max_spring, temperature_max_summer, temperature_max_autumn, temperature_min_winter, temperature_min_spring, temperature_min_summer, temperature_min_autumn, rainfall_winter, rainfall_spring, rainfall_summer, rainfall_autumn, wind_speed_10m, soil_moisture_surface, cloud_amount, wind_speed_range_2m, surface_pressure, specific_humidity_mean, temperature_mean, temperature_seasonal_range, rainfall_mean, rainfall_total_proxy, target_crop

## Cleaning Notes

- Columns were standardized to snake_case.
- Soil color strings were normalized into a compact categorical vocabulary.
- Target labels were whitespace-normalized and title-cased.
- Rows with the non-crop label 'Fallow' were removed because they do not represent a vegetation/crop recommendation target.
- No duplicate rows remained after cleaning.
- Domain validation was applied for pH, rainfall, soil moisture, and nutrient non-negativity.
- Outliers were retained unless they violated hard domain rules because extreme agronomic values may still be valid observations.
- The recommended `final_dataset.csv` uses the summary-feature variant because it delivered stronger validation and hold-out macro F1 than the full extended feature set in baseline experiments.