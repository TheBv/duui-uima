StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")
JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
AudioWav = luajava.bindClass("org.texttechnologylab.annotation.AudioWav")

function serialize(inputCas, outputStream, params)
    local doc_lang = inputCas:getDocumentLanguage()
    local audios = {}

    local model = params["model"] or "base"

    local audio_it = JCasUtil:select(inputCas, AudioWav):iterator()
    local audios_count = 1

    while audio_it:hasNext() do
        local audio = audio_it:next()
        local a = {
            text = audio:getCoveredText(),
            base64 = audio:getBase64(),
            channels = audio:getChannels(),
            frequence = audio:getFrequence(),
            bitsPerSample = audio:getBitsPerSample(),
            begin = audio:getBegin(),
            ['end'] = audio:getEnd(),
            id = audio:getTypeIndexID()
        }
        audios[audios_count] = a
        audios_count = audios_count + 1
    end
    
    outputStream:write(json.encode({
        audios = audios,
        lang = doc_lang,
        model= model
    }))
end

function find_audio_by_id(inputCas, id)
    local audio_it = JCasUtil:select(inputCas, AudioWav):iterator()

    while audio_it:hasNext() do
        local audio = audio_it:next()
        if audio:getTypeIndexID() == id then
            return audio
        end
    end

    return nil
end


function deserialize(inputCas, inputStream)
    local inputString = luajava.newInstance("java.lang.String", inputStream:readAllBytes(), StandardCharsets.UTF_8)
    local results = json.decode(inputString)

    if results["modification_meta"] ~= nil and results["transcripts"] ~= nil then
        for j, modification_meta in ipairs(results["modification_meta"]) do
            local modification_anno = luajava.newInstance("org.texttechnologylab.annotation.DocumentModification", inputCas)
            modification_anno:setUser(modification_meta["user"])
            modification_anno:setTimestamp(modification_meta["timestamp"])
            modification_anno:setComment(modification_meta["comment"])

            modification_anno:addToIndexes()
        end

        for j, transcription in ipairs(results["transcripts"]) do
            local transcription_anno = luajava.newInstance("org.texttechnologylab.annotation.Transcription", inputCas)
            transcription_anno:setBegin(transcription["begin"])
            transcription_anno:setEnd(transcription["end"])
            transcription_anno:setStartTime(transcription["startTime"])
            transcription_anno:setEndTime(transcription["endTime"])
            transcription_anno:setSpeaker(transcription["speaker"])
            transcription_anno:setUtterance(transcription["utterance"])
            transcription_anno:setModel(transcription["model"])
            transcription_anno:setReference(find_audio_by_id(inputCas, transcription["audio_wav_id"]))
            transcription_anno:addToIndexes()
        end
    end

end
