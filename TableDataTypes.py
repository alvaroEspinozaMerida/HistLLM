schema_types = {
    "historical_figures": {
        "curid": "Int64",
        "name": "string",
        "birth_year": "Int64",
        "birth_city": "string",
        "country": "string",
        "continent": "string",
        "occupation": "string",
        "industry": "string",
        "domain": "string",
        "gender": "string"
    },

    "historical_events_core": {
        "id": "Int64",
        "event_name": "string",
        "day": "Int64",
        "month": "Int64",
        "year": "Int64",
        "country": "string",
        "event_type": "string",
        "place_name": "string",
        "impact": "string",
        "affected_population": "string",
        "responsible_entity": "string",
        "outcome": "string"
    },

    "qa_pairs": {
        "id": "Int64",
        "question": "string",
        "answer": "string",
        "dataset_name": "string",
        "time_period": "string"
    }
}