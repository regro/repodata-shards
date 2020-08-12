import os
import requests
import rapidjson as json
import tqdm


def get_shard_path(subdir, pkg, n_dirs=12):
    chars = [c for c in pkg if c.isalnum()]
    while len(chars) < n_dirs:
        chars.append("z")

    pth_parts = (
        ["shards", subdir]
        + [chars[i] for i in range(n_dirs)]
        + [pkg + ".json"]
    )

    return os.path.join(*pth_parts)


if __name__ == "__main__":
    label = "main"
    for subdir in ["linux-64", "osx-64", "win-64", "linux-aarch64", "linux-ppc64le"]:
        r = requests.get(
            f"https://conda.anaconda.org/conda-forge/{subdir}/repodata.json"
        )
        rd = r.json()

        os.makedirs(f"shards/{subdir}", exist_ok=True)

        for pkg, attrs in tqdm.tqdm(rd["packages"].items(), desc=f"{subdir}"):
            subdir_pkg = os.path.join(subdir, pkg)
            url = f"https://conda.anaconda.org/conda-forge/{subdir_pkg}"
            shard = {}
            shard["labels"] = [label]
            shard["repodata_version"] = rd["repodata_version"]
            shard["repodata"] = attrs
            shard["subdir"] = subdir
            shard["package"] = pkg
            shard["url"] = url
            shard["feedstock"] = None

            pth = get_shard_path(subdir, pkg)
            dir = os.path.dirname(pth)
            os.makedirs(dir, exist_ok=True)

            with open(pth, "w") as fp:
                json.dump(shard, fp)
