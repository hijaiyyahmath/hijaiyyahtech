// src/lib/loadContent.ts
import releaseMatrix from "@/content/release_matrix.json";
import datasets from "@/content/datasets.json";

export type ReleaseMatrix = typeof releaseMatrix;
export type DatasetsDoc = typeof datasets;

export function getReleaseMatrix(): ReleaseMatrix {
    return releaseMatrix;
}

export function getDatasets(): DatasetsDoc {
    return datasets;
}
