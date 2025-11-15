import pytest
import json
from shadow_lambda import CompareOptions, JsonComparator

def _collect_issues(diffs):
    return [d["issue"] for d in diffs]

NEXTGEN_RESPONSE = json.loads(
    """
{
    "status": true,
    "data": {
        "baseScoreParameters": [
            {
                "regionId": "0dd7b7de-bdf8-47e2-8e76-4df27d578511",
                "irrigationCondition": true,
                "croppingIntensity": 2,
                "landUseType": "Agricultural"
            }
        ],
        "satScore": {
            "baseScore": 171,
            "kharifScore": 219,
            "overallScore": 580,
            "rabiScore": 190
        },
        "farmDetails": [
            {
                "regionId": "0dd7b7de-bdf8-47e2-8e76-4df27d578511",
                "surveyLabel": "B - 1",
                "regionDetails": "Telangana, Jagtial, Beerpur, Cherlapalle",
                "surveyDetails": "Survey Number - 106/1/10",
                "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                "surveyArea": 16597.33
            }
        ],
        "farmerCroppingHistory": {
            "K023": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3327.08,
                    "farmPotentialYield": 3039,
                    "performance": "Good",
                    "price": 2060
                }
            ],
            "R022": [
                {
                    "cropName": "Maize",
                    "districtThresholdYield": 4771.38,
                    "farmPotentialYield": 2420,
                    "performance": "Below Average",
                    "price": 1870
                },
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 2714.04,
                    "farmPotentialYield": 2575,
                    "performance": "Below Average",
                    "price": 1960
                }
            ],
            "R024": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 2916.55,
                    "farmPotentialYield": 3052,
                    "performance": "Average",
                    "price": 2183
                }
            ],
            "R023": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3000.34,
                    "farmPotentialYield": 3153,
                    "performance": "Good",
                    "price": 2060
                }
            ],
            "K024": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3410.55,
                    "farmPotentialYield": 3607,
                    "performance": "Good",
                    "price": 2183
                }
            ],
            "K022": [
                {
                    "cropName": "Cotton(lint)",
                    "districtThresholdYield": 1022.99,
                    "farmPotentialYield": 1200,
                    "performance": "Below Average",
                    "price": 5726
                },
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3220.15,
                    "farmPotentialYield": 2999,
                    "performance": "Good",
                    "price": 1960
                }
            ]
        },
        "majorCrops": {
            "state": [
                {
                    "name": "Telangana",
                    "district": [
                        {
                            "name": "Jagtial",
                            "seasons": {
                                "kharif": [
                                    {
                                        "cropName": "Paddy",
                                        "area": 64887,
                                        "yield": 3809,
                                        "cropPercentage": 38.45
                                    },
                                    {
                                        "cropName": "Maize",
                                        "area": 22255,
                                        "yield": 5553,
                                        "cropPercentage": 13.19
                                    },
                                    {
                                        "cropName": "Turmeric",
                                        "area": 13393,
                                        "yield": 7879,
                                        "cropPercentage": 7.94
                                    },
                                    {
                                        "cropName": "Cotton(lint)",
                                        "area": 10130,
                                        "yield": 461,
                                        "cropPercentage": 6
                                    }
                                ],
                                "rabi": [
                                    {
                                        "cropName": " Rice",
                                        "area": 105348,
                                        "yield": 3913,
                                        "cropPercentage": 62.43
                                    },
                                    {
                                        "cropName": "Paddy",
                                        "area": 66523,
                                        "yield": 3700,
                                        "cropPercentage": 39.42
                                    },
                                    {
                                        "cropName": "Maize",
                                        "area": 8803,
                                        "yield": 4861,
                                        "cropPercentage": 5.22
                                    },
                                    {
                                        "cropName": " Sesamum",
                                        "area": 8170,
                                        "yield": 780,
                                        "cropPercentage": 4.84
                                    }
                                ],
                                "horticulture": null,
                                "kharif_horticulture": null
                            },
                            "totalAgriArea": 168738.5269
                        }
                    ]
                }
            ]
        },
        "regionalParameters": {
            "nearestMandi": {
                "name": "Dharmapuri",
                "distance": 13.95
            },
            "nearestRoadRail": {
                "name": null,
                "distance": 2.03
            },
            "nearestWaterBody": {
                "name": null,
                "distance": 0.73
            },
            "droughtInstances": [
                2011,
                2012,
                2015,
                2016
            ],
            "temperature": {
                "min": 12.478448867797852,
                "max": 40.248619079589844
            },
            "regionalProsperity": 0.51,
            "villagePopulation": {
                "name": "Cherlapalle",
                "femalePopulation": null,
                "malePopulation": null,
                "totalPopulation": null
            },
            "soilType": "Mixed Red and Black Soils",
            "agroEcologicalSubZone": "DECCAN PLATEAU  (TELANGANA) AND EASTERN GHATS  HOT SEMI ARID ECO-REGION"
        },
        "waterConditions": {
            "state": [
                {
                    "name": "Telangana",
                    "district": [
                        {
                            "name": "Jagtial",
                            "subDistrict": [
                                {
                                    "name": "Beerpur",
                                    "rainfall": {
                                        "average": 1640,
                                        "yearlyData": {
                                            "2015": 1361,
                                            "2016": 2025,
                                            "2017": 1175,
                                            "2018": 1996,
                                            "2019": 1467,
                                            "2020": 1612,
                                            "2021": 1293,
                                            "2022": 2724,
                                            "2023": 1601,
                                            "2024": 1149
                                        }
                                    },
                                    "groundWater": {
                                        "average": 713,
                                        "yearlyData": {
                                            "2015": 664,
                                            "2016": 691,
                                            "2017": 676,
                                            "2018": 680,
                                            "2019": 689,
                                            "2020": 742,
                                            "2021": 726,
                                            "2022": 785,
                                            "2023": 717,
                                            "2024": 756
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "farmGeometry": [
            {
                "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                "geometryLabel": "1",
                "farmImage": "https://media.satsure.co/sage/satsource-report/f6c89060-1e97-4280-904c-b8f3a5596d36/testing_01/1-A.jpg",
                "geometryDetails": "Survey Number - 106/1/10",
                "subGeometry": [
                    {
                        "label": "1-A",
                        "centroid": {
                            "lon": {
                                "label": "E",
                                "value": 78.97
                            },
                            "lat": {
                                "label": "N",
                                "value": 19
                            }
                        },
                        "geometry": {
                            "GeoJSON": {
                                "type": "MultiPolygon",
                                "coordinates": [
                                    [
                                        [
                                            [
                                                78.965628993,
                                                19.000491424
                                            ],
                                            [
                                                78.965592873,
                                                19.000358437
                                            ],
                                            [
                                                78.96556297,
                                                19.000142625
                                            ],
                                            [
                                                78.965558543,
                                                18.999947818
                                            ],
                                            [
                                                78.965518738,
                                                18.999797394
                                            ],
                                            [
                                                78.965311225,
                                                18.99896421
                                            ],
                                            [
                                                78.965245322,
                                                18.99847264
                                            ],
                                            [
                                                78.965264391,
                                                18.998326751
                                            ],
                                            [
                                                78.965111928,
                                                18.998352705
                                            ],
                                            [
                                                78.964854214,
                                                18.99843353
                                            ],
                                            [
                                                78.96474083,
                                                18.998435963
                                            ],
                                            [
                                                78.964794939,
                                                18.998613749
                                            ],
                                            [
                                                78.964895104,
                                                18.999442999
                                            ],
                                            [
                                                78.9649591,
                                                19.000783676
                                            ],
                                            [
                                                78.965628993,
                                                19.000491424
                                            ]
                                        ]
                                    ]
                                ]
                            }
                        }
                    }
                ]
            }
        ],
        "metadata": {
            "referenceId": "testing_01",
            "reportDate": "2025-09-03",
            "requestId": "f23ae486-3492-4fcd-bd43-30783f03f8bd"
        },
        "neighboringGeometry": [
            [
                {
                    "id": "1",
                    "geometryId": null,
                    "details": null,
                    "direction": null,
                    "centroid": {
                        "coordinates": [
                            null,
                            null
                        ],
                        "type": "Point"
                    }
                }
            ]
        ]
    }
}
"""
)

LEGACY_RESPONSE = json.loads(
    """
{
    "data": {
        "baseScoreParameters": [
            {
                "croppingIntensity": 2,
                "irrigationCondition": true,
                "landUseType": "Agricultural",
                "regionId": "0dd7b7de-bdf8-47e2-8e76-4df27d578511"
            }
        ],
        "farmDetails": [
            {
                "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                "regionDetails": "Telangana, Jagtial, Beerpur, Cherlapalle",
                "regionId": "0dd7b7de-bdf8-47e2-8e76-4df27d578511",
                "surveyArea": 1.48,
                "surveyDetails": "Survey Number - 106/1/10",
                "surveyLabel": "BNone"
            }
        ],
        "farmGeometry": [
            {
                "farmImage": "https://media.satsure.co/sage/satsource-report/165358e3-2a85-4646-bfb6-262ac5996dd6/testing_01/1-A.jpg",
                "geometryDetails": "Survey Number - 106/1",
                "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                "geometryLabel": "1",
                "subGeometry": [
                    {
                        "centroid": {
                            "lat": {
                                "label": "N",
                                "value": 18.999597451782027
                            },
                            "lon": {
                                "label": "E",
                                "value": 78.96516491892413
                            }
                        },
                        "label": "1-A"
                    }
                ]
            }
        ],
        "farmPhenology": [
            {
                "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                "health": {
                    "2024-05-01": 0.237,
                    "2024-05-11": 0.175,
                    "2024-05-21": 0.104,
                    "2024-06-01": 0.056,
                    "2024-06-11": 0.057,
                    "2024-06-21": 0.075,
                    "2024-07-01": 0.069,
                    "2024-08-21": 0.167,
                    "2024-09-21": 0.348,
                    "2024-10-01": 0.472,
                    "2024-10-11": 0.404,
                    "2024-10-21": 0.324,
                    "2024-11-01": 0.31,
                    "2024-11-11": 0.312,
                    "2024-11-21": 0.248,
                    "2024-12-01": 0.121,
                    "2024-12-11": 0.074,
                    "2024-12-21": 0.073,
                    "2025-01-01": 0.101,
                    "2025-01-11": 0.072,
                    "2025-01-21": 0.086,
                    "2025-02-01": 0.106,
                    "2025-02-11": 0.199,
                    "2025-02-21": 0.271,
                    "2025-03-01": 0.338,
                    "2025-03-11": 0.35,
                    "2025-03-21": 0.371,
                    "2025-04-01": 0.369,
                    "2025-04-11": 0.355,
                    "2025-04-21": 0.308
                },
                "moisture": {
                    "2024-05-01": 0.31,
                    "2024-05-11": 0.043,
                    "2024-05-21": 0.15,
                    "2024-10-01": 0.34,
                    "2024-10-11": 0.455,
                    "2024-10-21": 0.391,
                    "2024-11-01": 0.386,
                    "2024-11-11": 0.346,
                    "2024-11-21": 0.214,
                    "2024-12-01": 0.108,
                    "2024-12-11": 0.062,
                    "2024-12-21": 0.062,
                    "2025-01-01": 0.059,
                    "2025-01-11": 0.115,
                    "2025-01-21": 0.196,
                    "2025-02-01": 0.273,
                    "2025-02-11": 0.306,
                    "2025-02-21": 0.323,
                    "2025-03-01": 0.352,
                    "2025-03-11": 0.375,
                    "2025-03-21": 0.393,
                    "2025-04-01": 0.401,
                    "2025-04-11": 0.39,
                    "2025-04-21": 0.34
                }
            }
        ],
        "farmerCroppingHistory": {
            "K022": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3220.15,
                    "farmPotentialYield": 3015,
                    "performance": "Good",
                    "price": 1960
                },
                {
                    "cropName": "Cotton(lint)",
                    "districtThresholdYield": 1022.99,
                    "farmPotentialYield": 1214,
                    "performance": "Below Average",
                    "price": 5726
                }
            ],
            "K023": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3327.08,
                    "farmPotentialYield": 3015,
                    "performance": "Good",
                    "price": 2060
                }
            ],
            "K024": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3410.55,
                    "farmPotentialYield": 3578,
                    "performance": "Good",
                    "price": 2183
                }
            ],
            "R023": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 3000.34,
                    "farmPotentialYield": 3176,
                    "performance": "Good",
                    "price": 2060
                }
            ],
            "R024": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 2916.55,
                    "farmPotentialYield": 3015,
                    "performance": "Average",
                    "price": 2183
                }
            ],
            "R025": [
                {
                    "cropName": "Paddy",
                    "districtThresholdYield": 2825.83,
                    "farmPotentialYield": 2934,
                    "performance": "Good",
                    "price": 2300
                }
            ]
        },
        "majorCrops": {
            "state": [
                {
                    "district": [
                        {
                            "name": "Jagtial",
                            "seasons": {
                                "horticulture": null,
                                "kharif": [
                                    {
                                        "area": 64887,
                                        "cropName": "Paddy",
                                        "cropPercentage": 38.45,
                                        "yield": 3809
                                    },
                                    {
                                        "area": 22255,
                                        "cropName": "Maize",
                                        "cropPercentage": 13.19,
                                        "yield": 5553
                                    },
                                    {
                                        "area": 13393,
                                        "cropName": "Turmeric",
                                        "cropPercentage": 7.94,
                                        "yield": 7879
                                    },
                                    {
                                        "area": 10130,
                                        "cropName": "Cotton(lint)",
                                        "cropPercentage": 6,
                                        "yield": 461
                                    }
                                ],
                                "kharif_horticulture": null,
                                "rabi": [
                                    {
                                        "area": 105348,
                                        "cropName": " Rice",
                                        "cropPercentage": 62.43,
                                        "yield": 3913
                                    },
                                    {
                                        "area": 66523,
                                        "cropName": "Paddy",
                                        "cropPercentage": 39.42,
                                        "yield": 3700
                                    },
                                    {
                                        "area": 8803,
                                        "cropName": "Maize",
                                        "cropPercentage": 5.22,
                                        "yield": 4861
                                    },
                                    {
                                        "area": 8170,
                                        "cropName": " Sesamum",
                                        "cropPercentage": 4.84,
                                        "yield": 780
                                    }
                                ]
                            },
                            "totalAgriArea": 168738.5269
                        }
                    ],
                    "name": "Telangana"
                }
            ]
        },
        "metadata": {
            "referenceId": "testing_01",
            "reportDate": "2025-09-04",
            "requestId": "f23ae486-3492-4fcd-bd43-30783f03f8bd",
            "yearsReported": [
                "2022-2021",
                "2021-2020",
                "2020-2019"
            ]
        },
        "neighboringGeometry": [
            [
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49అ1",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "1"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49అ2",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "2"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49అ3",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "3"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49అ4",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "4"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49అ5",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "5"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49ఆ",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "6"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49ఇ/1",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "7"
                },
                {
                    "centroid": {
                        "coordinates": [
                            78.96690675772422,
                            18.99901303168989
                        ],
                        "type": "Point"
                    },
                    "details": "Survey Number - 49ఇ/2",
                    "direction": "East",
                    "geometryId": "0dd7b7de-1b95-4235-94d5-f71ce47955cc",
                    "id": "8"
                }
            ]
        ],
        "regionalParameters": {
            "agroEcologicalSubZone": "Deccan Plateau  (Telangana) And Eastern Ghats  Hot Semi Arid Eco-Region",
            "droughtInstances": [
                2011,
                2012,
                2015,
                2016
            ],
            "nearestMandi": {
                "distance": 14.7,
                "name": "Dharmapuri"
            },
            "nearestRoadRail": {
                "distance": 2.2,
                "name": null
            },
            "nearestWaterBody": {
                "distance": 0.8,
                "name": ""
            },
            "regionalProsperity": 0.51,
            "soilType": "Mixed Red and Black Soils",
            "temperature": {
                "max": 40.2,
                "min": 12.5
            },
            "villagePopulation": {
                "femalePopulation": null,
                "malePopulation": null,
                "name": "Cherlapalle",
                "totalPopulation": null
            }
        },
        "satScore": {
            "baseScore": 200,
            "kharifScore": 297,
            "overallScore": 828,
            "rabiScore": 331
        },
        "waterConditions": {
            "state": [
                {
                    "district": [
                        {
                            "name": "Jagtial",
                            "subDistrict": [
                                {
                                    "groundWater": {
                                        "average": 713,
                                        "yearlyData": {
                                            "2015": 665,
                                            "2016": 692,
                                            "2017": 676,
                                            "2018": 681,
                                            "2019": 690,
                                            "2020": 743,
                                            "2021": 726,
                                            "2022": 785,
                                            "2023": 717,
                                            "2024": 756
                                        }
                                    },
                                    "name": "Beerpur",
                                    "rainfall": {
                                        "average": 1640,
                                        "yearlyData": {
                                            "2015": 1362,
                                            "2016": 2026,
                                            "2017": 1175,
                                            "2018": 1996,
                                            "2019": 1467,
                                            "2020": 1612,
                                            "2021": 1294,
                                            "2022": 2724,
                                            "2023": 1602,
                                            "2024": 1150
                                        }
                                    }
                                }
                            ]
                        }
                    ],
                    "name": "Telangana"
                }
            ]
        }
    },
    "status": true
}
"""
)

def test_unordered_lists_surface_nested_differences():
    comparator = JsonComparator(CompareOptions(list_mode="unordered"))
    satsource = [
        {"id": "farm-002", "metrics": {"yield": 1.1, "history": [1, 2]}},
        {"id": "farm-001", "metrics": {"yield": 2.2, "history": [3, 4]}},
    ]
    legacy = [
        {"id": "farm-001", "metrics": {"yield": 2.2, "history": [3, 5]}},
        {"id": "farm-002", "metrics": {"yield": 1.1, "history": [1, 2]}},
    ]

    comparator.compare(satsource, legacy)
    diffs = comparator.result()["differences"]

    nested_paths = {d["path"] for d in diffs}
    assert "$[0].metrics.history[1]" in nested_paths

    issues = _collect_issues(diffs)
    assert any("extra element in A" in issue for issue in issues)
    assert any("missing element in A" in issue for issue in issues)


def test_unordered_lists_still_report_unmatched_elements():
    comparator = JsonComparator(CompareOptions(list_mode="unordered"))
    satsource = [
        {"id": "only-in-satsource"},
        {"id": "shared", "data": 1},
    ]
    legacy = [
        {"id": "shared", "data": 2},
        {"id": "only-in-legacy"},
    ]

    comparator.compare(satsource, legacy)
    diffs = comparator.result()["differences"]

    issues = _collect_issues(diffs)
    assert any("extra element in A" in issue for issue in issues)
    assert any("missing element in A" in issue for issue in issues)
    assert any(issue.startswith("number mismatch") for issue in issues)

def _run_comparison(list_mode: str = "ordered"):
    options = CompareOptions(list_mode=list_mode, label_a="satsource", label_b="legacy")
    comparator = JsonComparator(options)
    comparator.compare(NEXTGEN_RESPONSE, LEGACY_RESPONSE, "$")
    return comparator.result()["differences"]


def test_missing_key_message_references_domain_labels():
    diffs = _run_comparison()
    assert any(
        diff["path"] == "$.data"
        and diff["issue"] == "missing key in satsource (present in legacy): farmPhenology"
        for diff in diffs
    ), "Expected missing farmPhenology diff with satsource/legacy labels"


def test_ordered_list_length_diff_mentions_both_labels():
    diffs = _run_comparison()
    assert any(
        diff["path"] == "$.data.neighboringGeometry[0]"
        and "satsource has 1 items" in diff["issue"]
        and "legacy has 8 items" in diff["issue"]
        for diff in diffs
    ), "Expected neighboringGeometry length diff that cites satsource vs legacy"


def test_unordered_list_element_diff_mentions_both_labels():
    diffs = _run_comparison(list_mode="unordered")
    assert any(
        "missing element in satsource (present in legacy)" in diff["issue"]
        for diff in diffs
    ), "Expected at least one unordered list diff mentioning satsource vs legacy"
