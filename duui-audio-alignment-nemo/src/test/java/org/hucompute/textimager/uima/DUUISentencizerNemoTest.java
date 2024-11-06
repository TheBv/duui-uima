package org.hucompute.textimager.uima;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import org.apache.commons.io.FileUtils;
import org.apache.uima.UIMAException;
import org.apache.uima.fit.factory.JCasFactory;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.util.XmlCasSerializer;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.texttechnologylab.DockerUnifiedUIMAInterface.DUUIComposer;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIDockerDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIRemoteDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaContext;
import org.texttechnologylab.annotation.*;
import org.xml.sax.SAXException;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class DUUISentencizerNemoTest {
    static DUUIComposer composer;
    static JCas cas;

    // TODO does not restart!?
    private static Stream<String> dockerImages() {
        return Stream.of(
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-ruler:latest",
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-senter-sm:latest"
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-senter-md:latest"
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-senter-lg:latest"
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-parser-sm:latest"
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-parser-md:latest"
                //"docker.texttechnologylab.org/duui-sentencizer-spacy-parser-lg:latest"
                // "docker.texttechnologylab.org/duui-sentencizer-spacy-trf:latest"
        );
    }

    /*@BeforeAll
    static void beforeAll() throws URISyntaxException, IOException, UIMAException, SAXException {
        composer = new DUUIComposer()
                .withSkipVerification(true)
                .withLuaContext(new DUUILuaContext().withJsonLibrary());

        DUUIDockerDriver dockerDriver = new DUUIDockerDriver();
        composer.addDriver(dockerDriver);

        cas = JCasFactory.createJCas();
    }

    @AfterAll
    static void afterAll() throws UnknownHostException {
        composer.shutdown();
    }

    @AfterEach
    public void afterEach() throws IOException, SAXException {
        composer.resetPipeline();

        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        XmlCasSerializer.serialize(cas.getCas(), null, stream);
        System.out.println(stream.toString(StandardCharsets.UTF_8));

        cas.reset();
    }*/

    public void createCas(String language, List<String> sentences) {
        cas.setDocumentLanguage(language);

        StringBuilder sb = new StringBuilder();
        if (sentences != null) {
            for (String sentence : sentences) {
                sb.append(sentence).append(" ");
            }
        }

        cas.setDocumentText(sb.toString());
    }

    @Test
    public void testTest() throws Exception {
        composer = new DUUIComposer()
                .withSkipVerification(true)
                .withLuaContext(new DUUILuaContext().withJsonLibrary());
        composer.addDriver(new DUUIRemoteDriver());
        composer.add(
                new DUUIRemoteDriver
                        .Component("http://127.0.0.1:1001")
                        .withScale(1)
        );
        composer.add(
                new DUUIRemoteDriver
                        .Component("http://127.0.0.1:1000")
                        .withScale(1)
        );
        cas = JCasFactory.createJCas();
        cas.setDocumentLanguage("de");
        cas.setDocumentText("Example text");


        String base64 = Base64.getEncoder().encodeToString(FileUtils.readFileToByteArray(new File("src/test/resources/output_3.wav")));
        

        

        AudioWav audioWave = new AudioWav(cas);
        audioWave.setBegin(0);
        audioWave.setEnd(cas.getDocumentText().length());
        audioWave.setChannels(1);

        audioWave.setFrequence(16000);
        audioWave.setBitsPerSample(16);
        audioWave.setBase64(base64);
        audioWave.addToIndexes();

        composer.run(cas);
        cas.getViewName();
        JCasUtil.select(cas, DocumentModification.class).forEach(System.out::println);
    }

    @ParameterizedTest
    @MethodSource("dockerImages")
    public void sentencesTest(String dockerImage) throws Exception {
        composer.add(
                new DUUIDockerDriver.Component(dockerImage)
                        .withImageFetching()
        );

        List<String> expectedSentences = Arrays.asList(
                "This is a very great example sentence!",
                "I absolutely hate this example."
        );
        Integer[] expectedSentenceSpansBegin = new Integer[]{ 0, 39 };
        Integer[] expectedSentenceSpansEnd = new Integer[]{ 38, 70 };

        createCas("en", expectedSentences);
        composer.run(cas);

        Collection<AnnotatorMetaData> actualAnnotatorMetaDatas = new ArrayList<>(JCasUtil.select(cas, AnnotatorMetaData.class));
        assertEquals(expectedSentences.size(), actualAnnotatorMetaDatas.size());

        Collection<DocumentModification> actualDocumentModifications = new ArrayList<>(JCasUtil.select(cas, DocumentModification.class));
        assertEquals(1, actualDocumentModifications.size());

        Collection<Sentence> actualSentences = new ArrayList<>(JCasUtil.select(cas, Sentence.class));
        assertEquals(expectedSentences.size(), actualSentences.size());

        Integer[] actualSenttencesSpansBegin = actualSentences.stream().map(Sentence::getBegin).toArray(Integer[]::new);
        assertArrayEquals(expectedSentenceSpansBegin, actualSenttencesSpansBegin);

        Integer[] actualSenttencesSpansEnd = actualSentences.stream().map(Sentence::getEnd).toArray(Integer[]::new);
        assertArrayEquals(expectedSentenceSpansEnd, actualSenttencesSpansEnd);
    }

    @ParameterizedTest
    @MethodSource("dockerImages")
    public void emptyTest(String dockerImage) throws Exception {
        composer.add(
                new DUUIDockerDriver.Component(dockerImage)
                        .withImageFetching()
        );

        createCas("en", null);
        composer.run(cas);

        Collection<AnnotatorMetaData> actualAnnotatorMetaDatas = new ArrayList<>(JCasUtil.select(cas, AnnotatorMetaData.class));
        assertEquals(0, actualAnnotatorMetaDatas.size());

        Collection<DocumentModification> actualDocumentModifications = new ArrayList<>(JCasUtil.select(cas, DocumentModification.class));
        assertEquals(1, actualDocumentModifications.size());

        Collection<Sentence> actualSentences = new ArrayList<>(JCasUtil.select(cas, Sentence.class));
        assertEquals(0, actualSentences.size());
    }
}
