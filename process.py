import json
import pandas as pd


def format_record(inputRecord):
    return_record = {
        "frequency": {"start": inputRecord["start"], "end": inputRecord["end"]},
        "allocation": {
            "amateur": {
                "status": inputRecord["Amateur allocation"],
                "comment": inputRecord["Amateur allocation comment"],
            },
            "amateurSatellite": {
                "status": inputRecord["Amateur Satellite allocation"],
                "comment": inputRecord["Amateur Satellite allocation comment"],
            },
        },
        "power": {
            "normal": inputRecord["Maximum Peak Envelope Power"],
            "airborne": inputRecord["Airborne"],
        },
        "meta": {"preferredUnits": inputRecord["units"]},
    }

    return return_record


def process_csv(inputCsvPath):
    ## read in file
    in_df = pd.read_csv(inputCsvPath)

    ## parse out the preferred units
    in_df["units"] = in_df["Frequency band end"].apply(lambda x: x.split(" ")[-1])

    ## parse out the start and end frequencies
    ## and convert them to hertz
    in_df["Frequency band end"] = (
        in_df["Frequency band end"].apply(lambda x: x.split(" ")[0]).astype(float)
    )

    in_df["start"] = in_df.apply(
        lambda x: x["Frequency band start"]
        * (
            1000
            if x.units == "kHz"
            else 1000000 if x.units == "MHz" else 1000000000 if x.units == "GHz" else 0
        ),
        axis=1,
    ).astype(int)

    in_df["end"] = in_df.apply(
        lambda x: x["Frequency band end"]
        * (
            1000
            if x.units == "kHz"
            else 1000000 if x.units == "MHz" else 1000000000 if x.units == "GHz" else 0
        ),
        axis=1,
    ).astype(int)

    ## drop the original frequency columns
    in_df = in_df.drop(["Frequency band start", "Frequency band end"], axis=1)

    ## build up a dict
    in_df["record"] = in_df.apply(format_record, axis=1)

    ## combine all the dicts into one
    compiled_records = {band: list(df["record"]) for band, df in in_df.groupby("Band")}

    return compiled_records


if __name__ == "__main__":
    with open("res/foundation.json", "w") as outfile:
        outfile.write(json.dumps(process_csv("res/foundation_ofcom_data.csv"), indent=4))
