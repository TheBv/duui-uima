[![Version](https://img.shields.io/static/v1?label=duui-audio-alignment&message=0.1.2&color=blue)](https://docker.texttechnologylab.org/v2/duui-audio-alignment/tags/list)
[![Version](https://img.shields.io/static/v1?label=Python&message=3.8&color=green)]()
[![Version](https://img.shields.io/static/v1?label=Transformers&message=4.21.1&color=yellow)]()
[![Version](https://img.shields.io/static/v1?label=Torch&message=1.11.0&color=red)]()

# Audio Alignment

DUUI Audio Alignment methods.

## Included Models

| Name                                    | attractors |
| --------------------------------------- | -----------|
| SC_LibriSpeech_2spk | 10,20 |
| SC_LibriSpeech_2spk_adapted1-10 | 10,20 |
| SC_LibriSpeech_2spk_adapted1-10_finetuneAliMeetingNearmix |10,20  |


# How To Use

For using duui-audio-alignment as a DUUI image it is necessary to use the [Docker Unified UIMA Interface (DUUI)](https://github.com/texttechnologylab/DockerUnifiedUIMAInterface).

## Start Docker container

```
docker run --rm -p 1000:9714 docker.texttechnologylab.org/duui-audio-alignment:latest
```

Find all available image tags here: https://docker.texttechnologylab.org/v2/textimager-duui-audio-alignment/tags/list

## Run within DUUI

```
composer.add(
    new DUUIDockerDriver.Component("docker.texttechnologylab.org/textimager-duui-audio-alignment:latest")
        .withScale(iWorkers)
        .withImageFetching()
);
```

### Parameters

| Name | Description |
| ---- | ----------- |
| `model_name` | TODO |

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
  title          = {DiaPer model as DUUI component},
  year           = {2024},
  howpublished   = {https://github.com/texttechnologylab/duui-uima/tree/main/duui-audio-alignment}
}

```

