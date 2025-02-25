package org.hucompute.textimager.uima;

import org.apache.uima.analysis_component.AnalysisComponent_ImplBase;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.analysis_engine.impl.AnalysisEngineDescription_impl;
import org.apache.uima.analysis_engine.impl.AnalysisEngineImplBase;
import org.apache.uima.cas.AbstractCas;
import org.apache.uima.cas.FeatureStructure;
import org.apache.uima.fit.component.JCasConsumer_ImplBase;
import org.apache.uima.fit.descriptor.ResourceMetaData;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.cas.FSArray;
import org.apache.uima.resource.ResourceManager;
import org.apache.uima.resource.ResourceSpecifier;
import org.apache.uima.util.InvalidXMLException;
import org.json.JSONObject;
import org.junit.jupiter.api.Test;
import org.texttechnologylab.DockerUnifiedUIMAInterface.DUUIComposer;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIDockerDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIRemoteDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIUIMADriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.io.DUUIAsynchronousProcessor;
import org.texttechnologylab.DockerUnifiedUIMAInterface.io.reader.DUUIFileReader;
import org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaContext;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.dkpro.core.io.xmi.XmiWriter;
import org.texttechnologylab.DockerUnifiedUIMAInterface.pipeline_storage.sqlite.DUUISqliteStorageBackend;
import org.texttechnologylab.type.llm.prompt.FillableMessage;
import org.texttechnologylab.type.llm.prompt.Message;
import org.texttechnologylab.type.llm.prompt.Prompt;


import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import org.apache.uima.fit.descriptor.ResourceMetaData;
public class Jcal24Test {
    @Test
    public void testPrompt() throws Exception {
        long RANDOM_SEED = 1732975931;

        int runs = 5;
        for (int run = 0; run < runs; run++) {
            long local_seed = RANDOM_SEED + run;

//            String model = "llama3.2:3b-instruct-q4_K_M";
            // String model = "gemma2:27b-instruct-q4_0";
            // String model = "llama3.3:70b-instruct-q4_K_M";
            // String model = "nemotron:70b-instruct-q4_K_M";
            // String model = "deepseek-r1:70b";
            // String model = "mistral:7b-instruct-v0.3-q4_0";
            // String model = "mixtral:8x7b-instruct-v0.1-q4_0";
            // String model = "llama3.2:3b-instruct-fp16";
            String model = "minicpm-v:8b-2.6-fp16";

            Path baseDir = Paths.get("/storage/projects/baumartz/jcal_2024_textannotator/xmi/");
            String promptName = "ECO_IMAGES_SUMMARY";
            String promptVersion = "10";
            String task = "eco_nudging_images";
            String reasoningContexts = "PB";

            Path inDir = baseDir
                    .resolve(task)
                    .resolve("01_export")
                    .resolve(promptName)
                    .resolve(promptVersion);

            Path outDir = baseDir
                    .resolve(task)
                    .resolve("01_llm")
                    .resolve(task + "_" + reasoningContexts)
                    .resolve(promptName)
                    .resolve(promptVersion)
                    .resolve(model.replaceAll("/", "_").replace(":", "_"))
                    .resolve("run_" + run);
            Files.createDirectories(outDir);

            Path sqlitePath = outDir.resolve("_stats.db");
            DUUISqliteStorageBackend sqlite = new DUUISqliteStorageBackend(sqlitePath.toString())
                    .withConnectionPoolSize(1);

            DUUIComposer composer = new DUUIComposer()
                    .withWorkers(1)
                    .withSkipVerification(true)
                    .withStorageBackend(sqlite)
                    .withLuaContext(new DUUILuaContext().withJsonLibrary());

            DUUIDockerDriver dockerDriver = new DUUIDockerDriver();
            composer.addDriver(dockerDriver);
            DUUIUIMADriver uimaDriver = new DUUIUIMADriver();
            composer.addDriver(uimaDriver);
            DUUIRemoteDriver remoteDriver = new DUUIRemoteDriver();
            composer.addDriver(remoteDriver);

            String baseUrl = "host.docker.internal:12441";

            JSONObject llmArgsJson = new JSONObject();
            llmArgsJson.put("base_url", baseUrl);
            llmArgsJson.put("system", "geltlin.hucompute.org:12441");  // in case we use local port forwarding or similar...
            llmArgsJson.put("model", model);
            llmArgsJson.put("temperature", 0.8);
            llmArgsJson.put("num_ctx", 2048);
            llmArgsJson.put("num_predict", -2);
            llmArgsJson.put("seed", local_seed);
            llmArgsJson.put("keep_alive", 3600);
            llmArgsJson.put("format", "json");

            composer.add(
                    new DUUIRemoteDriver.Component("http://localhost:9716")
                            //new DUUIDockerDriver.Component("docker.texttechnologylab.org/duui-core-llm-rating:0.0.4")
                            .withParameter("llm_args", llmArgsJson.toString())
                            .withScale(1)
                            .build()
                            .withTimeout(1000000000L)
            );

            DUUIAsynchronousProcessor reader = new DUUIAsynchronousProcessor(new DUUIFileReader(
                    inDir.toString(),
                    ".xmi.gz",
                    1,
                    0,
                    false,
                    "",
                    false,
                    "de",
                    0,
                    outDir.toString(),
                    ".xmi.xmi.gz"
            ));
            if (promptName.contains("SUMMARY")) {
                composer.add(new DUUIUIMADriver.Component(createEngineDescription(JCasEdit.class)).build());
                composer.add(new DUUIRemoteDriver.Component("http://localhost:9716")
                        //new DUUIDockerDriver.Component("docker.texttechnologylab.org/duui-core-llm-rating:0.0.4")
                        .withParameter("llm_args", llmArgsJson.toString())
                        .withScale(1)
                        .build()
                        .withTimeout(1000000000L)
                );
            }
            composer.add(new DUUIUIMADriver.Component(createEngineDescription(XmiWriter.class
                    , XmiWriter.PARAM_TARGET_LOCATION, outDir.toString()
                    , XmiWriter.PARAM_PRETTY_PRINT, true
                    , XmiWriter.PARAM_OVERWRITE, true
                    , XmiWriter.PARAM_VERSION, "1.1"
                    , XmiWriter.PARAM_COMPRESSION, "GZIP"
            )).build());

            composer.run(reader, "llm");
            composer.shutdown();
        }
    }



}
