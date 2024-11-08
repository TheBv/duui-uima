StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")
Class = luajava.bindClass("java.lang.Class")
JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
DUUIUtils = luajava.bindClass("org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaUtils")
AudioWav = luajava.bindClass("org.texttechnologylab.annotation.AudioWav")

function serialize(inputCas, outputStream, parameters)
    local doc_lang = inputCas:getDocumentLanguage()
    local doc_len = DUUIUtils:getDocumentTextLength(inputCas)

    local audios = {}

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
        len = doc_len,
        lang = doc_lang
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

    if results["modification_meta"] ~= nil and results["rttms"] ~= nil then
        for j, modification_meta in ipairs(results["modification_meta"]) do
            local modification_anno = luajava.newInstance("org.texttechnologylab.annotation.DocumentModification", inputCas)
            modification_anno:setUser(modification_meta["user"])
            modification_anno:setTimestamp(modification_meta["timestamp"])
            modification_anno:setComment(modification_meta["comment"])

            modification_anno:addToIndexes()
        end

        for j, rttm in ipairs(results["rttms"]) do
            local rttm_anno = luajava.newInstance("org.texttechnologylab.annotation.RTTM", inputCas)
            rttm_anno:setSegmentType(rttm["segmentType"])
            rttm_anno:setChannel(rttm["channel"])
            rttm_anno:setTurnOnset(rttm["turnOnset"])
            rttm_anno:setTurnDuration(rttm["turnDuration"])
            rttm_anno:setOrthographyField(rttm["orthographyField"])
            rttm_anno:setSpeakerType(rttm["speakerType"])
            rttm_anno:setSpeakerName(rttm["speakerName"])
            rttm_anno:setConfidenceScore(rttm["confidenceScore"])
            rttm_anno:setSignalLookaheadTime(rttm["signalLookaheadTime"])
            rttm_anno:setModel(rttm["model"])
            rttm_anno:setReference(find_audio_by_id(inputCas, rttm["audio_wav_id"]))
            
            rttm_anno:addToIndexes()
        end
    end
end
