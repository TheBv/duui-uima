[![Version](https://img.shields.io/static/v1?label=duui-transcription-nemo&message=0.1&color=blue)](https://docker.texttechnologylab.org/v2/duui-transcription-nemo/tags/list)
[![Version](https://img.shields.io/static/v1?label=Python&message=3.10&color=green)]()
[![Version](https://img.shields.io/static/v1?label=Torch&message=2.2.1&color=red)]()
[![Version](https://img.shields.io/static/v1?label=NeMo&message=2.0.0rc1&color=yellow)]()
# Transformers Sentiment

DUUI implementation for selected Hugging-Face-based transformer [sentiment tools](https://huggingface.co/models?sort=trending&search=sentiment).

## Included ARPA Models for realignment

| Name                                    | Source                                 | 
| --------------------------------------- | ---------------------------------------- |
| KALDI Tedlium Language Models 4-Gram Big ARPA | https://kaldi-asr.org/models/m5 | 
| TODO: 4gram-pruned-0_11_17_21-de-lm-set-1.0.arpa | https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/speechtotext_de_de_lm/files | 

# How To Use

For using duui-audio-alignment-nemo as a DUUI image it is necessary to use the [Docker Unified UIMA Interface (DUUI)](https://github.com/texttechnologylab/DockerUnifiedUIMAInterface).

## Start Docker container

```
docker run --rm -p 1000:9714 docker.texttechnologylab.org/duui-audio-alignment-nemo:latest
```

Find all available image tags here: https://docker.texttechnologylab.org/v2/duui-audio-alignment-nemo/tags/list

## Run within DUUI

```
composer.add(
    new DUUIDockerDriver.Component("docker.texttechnologylab.org/duui-audio-alignment-nemo:latest")
        .withScale(iWorkers)
        .withImageFetching()
);
```


Note: you might need to add `--ipc=host` to the docker run command for memory sharing, depending on your setup

### Parameters

| Name | Description | Default |
| ---- | ----------- | ------- |
| `domain_type` | Either `meeting`, `telephonic` or `general` | `meeting` |
| `type` | Either `words` or `sentences` | `words`
| `realign_threshold`  | Float logprob_diff_threshold for ARPA alignment | `-1` (Disabled)  |

# Cite

If you want to use the DUUI image please quote this as follows:

Alexander Leonhardt, Giuseppe Abrami, Daniel Baumartz and Alexander Mehler. (2023). "Unlocking the Heterogeneous Landscape of Big Data NLP with DUUI." Findings of the Association for Computational Linguistics: EMNLP 2023, 385–399. [[LINK](https://aclanthology.org/2023.findings-emnlp.29)] [[PDF](https://aclanthology.org/2023.findings-emnlp.29.pdf)] 

## BibTeX

```
@inproceedings{Leonhardt:et:al:2023,
  title     = {Unlocking the Heterogeneous Landscape of Big Data {NLP} with {DUUI}},
  author    = {Leonhardt, Alexander and Abrami, Giuseppe and Baumartz, Daniel and Mehler, Alexander},
  editor    = {Bouamor, Houda and Pino, Juan and Bali, Kalika},
  booktitle = {Findings of the Association for Computational Linguistics: EMNLP 2023},
  year      = {2023},
  address   = {Singapore},
  publisher = {Association for Computational Linguistics},
  url       = {https://aclanthology.org/2023.findings-emnlp.29},
  pages     = {385--399},
  pdf       = {https://aclanthology.org/2023.findings-emnlp.29.pdf},
  abstract  = {Automatic analysis of large corpora is a complex task, especially
               in terms of time efficiency. This complexity is increased by the
               fact that flexible, extensible text analysis requires the continuous
               integration of ever new tools. Since there are no adequate frameworks
               for these purposes in the field of NLP, and especially in the
               context of UIMA, that are not outdated or unusable for security
               reasons, we present a new approach to address the latter task:
               Docker Unified UIMA Interface (DUUI), a scalable, flexible, lightweight,
               and feature-rich framework for automatic distributed analysis
               of text corpora that leverages Big Data experience and virtualization
               with Docker. We evaluate DUUI{'}s communication approach against
               a state-of-the-art approach and demonstrate its outstanding behavior
               in terms of time efficiency, enabling the analysis of big text
               data.}
}

@misc{Schrottenbacher:2024,
  author         = {Schrottenbacher, Patrick},
  title          = {NeMo Audio Alignment as DUUI component},
  year           = {2024},
  howpublished   = {https://github.com/texttechnologylab/duui-uima/tree/main/duui-audio-alignment-nemo}
}

```

