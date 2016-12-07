import pandas
import numpy as np
class CongressElection():
    def parse_file(self, filename, sheetname=""):
        with open(filename) as f:
            ds = pandas.read_excel(f, sheetname=sheetname, parse_cols="C,D,I,K,P")
            ds.rename(inplace=True, columns=lambda x: x.strip())
            ds.dropna(inplace=True, subset=["GENERAL VOTES", "CANDIDATE NAME"])
            ds = ds[~ds["CANDIDATE NAME"].isin(["Scattered"])]
            ds = ds[~ds["GENERAL VOTES"].isin(["#"])]
            ds.rename(columns={'D':'DISTRICT'}, inplace=True)
            ds["GENERAL VOTES"] = np.where(ds["GENERAL VOTES"] == "Unopposed", 0, ds["GENERAL VOTES"])
            self.df = ds
            return ds
    def calculate_wasted(self):
            # Work out wasted votes
            ds = self.df
            grouped = ds.groupby(["STATE","DISTRICT"])
            ds["max"] = grouped["GENERAL VOTES"].transform(lambda x: max(x))
            ds["wasted"] = np.where(ds["max"] != ds["GENERAL VOTES"], ds["GENERAL VOTES"], -1)
            ds["runnerup"] = ds.groupby(["STATE","DISTRICT"])["wasted"].transform(lambda x: max(x))
            # If effectively unopposed, the runner up should be 0.
            # This presents an issue with the model, in that yes this demonstrates
            ds["runnerup"] = np.where(ds["runnerup"] == -1, 0, ds["runnerup"])
            ds["win_count"] = np.where(ds["wasted"] == -1, 1, 0)
            ds["wasted"] = np.where(ds["wasted"] == -1, ds["GENERAL VOTES"] - ds["runnerup"], ds["wasted"])
            ds.drop('runnerup', 1, inplace=True)
            ds.drop('max', 1, inplace=True)
            self.df = ds
            return ds



if __name__ == '__main__':
    p = CongressElection()
    ds = p.parse_file("results14.xls", sheetname="2014 US House Results by State")
    ds = p.calculate_wasted()
    group = ds.groupby(["STATE", "PARTY"])
    ds["statewide_wasted_votes"] = group["wasted"].transform(lambda x: sum(x))
    ds["statewide_votes"] = group["GENERAL VOTES"].transform(lambda x: sum(x))
    ds["statewide_seats"] = group["win_count"].transform(lambda x: sum(x))
    ds.drop('CANDIDATE NAME', 1, inplace=True)
    ds.drop('DISTRICT', 1, inplace=True)
    ds.drop('GENERAL VOTES', 1, inplace=True)
    ds.drop('wasted', 1, inplace=True)
    ds.drop('win_count', 1, inplace=True)
    ds = ds.drop_duplicates()
    print ds
