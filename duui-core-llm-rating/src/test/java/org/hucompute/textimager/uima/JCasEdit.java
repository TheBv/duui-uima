package org.hucompute.textimager.uima;

import org.apache.uima.fit.component.JCasConsumer_ImplBase;
import org.apache.uima.fit.descriptor.ResourceMetaData;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.cas.FSArray;
import org.texttechnologylab.type.llm.prompt.FillableMessage;
import org.texttechnologylab.type.llm.prompt.Message;
import org.texttechnologylab.type.llm.prompt.Prompt;

import java.util.ArrayList;
import java.util.List;

@ResourceMetaData(
        name = "org.hucompute.textimager.uima.JCasEdit",
        description = "Base class for writers that write to the file system.",
        version = "1.0.0",
        vendor = "TTLab",
        copyright = "Copyright 2025\n            TTLab\n            Frankfurt University"
)
public class JCasEdit extends JCasConsumer_ImplBase {

    public JCasEdit() {

    }

    @Override
    public void process(JCas aJCas) {
        JCasUtil.select(aJCas, Prompt.class).forEach(prompt -> {
            FSArray<Message> messages = prompt.getMessages();
            List<Message> newMessages = new ArrayList<>();
            // copy all messages to list
            for (int i = 0; i < messages.size(); i++) {
                newMessages.add(messages.get(i));
            }
            Message summaryMessage = new Message(aJCas);
            summaryMessage.setContent(
                    """
                            Gebe nun deine Bewertung in einem einzigen, strikten, validen JSON Dictionary für Python ohne Kommentare aus, wobei die Keys
                            den Kriterien-IDs entsprechen müssen. Stelle sicher, dass die Schlüssel und Werte immer korrekt in Anführungszeichen gesetzt sind.
                            Das Dictionary darf ausschließlich die Bewertung enthalten.
                                                """
            );

            summaryMessage.addToIndexes();
            newMessages.add(summaryMessage);
            FillableMessage aiMessage = new FillableMessage(aJCas);
            aiMessage.setContent("\"\"");
            aiMessage.setContextName("llm_ratings");
            aiMessage.setClassModule("langchain_core.messages.ai");
            aiMessage.setClassName("AIMessage");
            aiMessage.addToIndexes();
            newMessages.add(aiMessage);
            prompt.setMessages(FSArray.create(aJCas, newMessages.toArray(new Message[0])));
            prompt.addToIndexes();
        });
    }
}
