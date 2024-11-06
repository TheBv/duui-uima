StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")
Class = luajava.bindClass("java.lang.Class")
JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
DUUIUtils = luajava.bindClass("org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaUtils")
AudioWav = luajava.bindClass("org.texttechnologylab.annotation.AudioWav")
Transcription = luajava.bindClass("org.texttechnologylab.annotation.Transcription")

function serialize(inputCas, outputStream, parameters)
    local doc_lang = inputCas:getDocumentLanguage()

    local domain_type = parameters["domain_type"]

    local realign_threshold = parameters["realign_threshold"]

    local type = parameters["type"]

    if domain_type == nil or domain_type == "" then
        domain_type = "meeting"
    end

    if realign_threshold == nil or realign_threshold == "" then
        realign_threshold = -1
    end

    if type == nil or type == "" then
        type = "words"
    end

    local align = {}
    local align_count = 1

    local audio_it = JCasUtil:select(inputCas, AudioWav):iterator()

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


        align[align_count] = {
            audio = a,
            transcriptions = find_transcriptions_by_id(inputCas, audio:getTypeIndexID())
        }
        align_count = align_count + 1
    end

    
    outputStream:write(json.encode({
        align = align,
        lang = doc_lang,
        realign_threshold = realign_threshold,
        domain_type = domain_type,
        type = type
    }))
end

function find_transcriptions_by_id(inputCas, id)
    local transcription_it = JCasUtil:select(inputCas, Transcription):iterator()

    local transcriptions = {}
    local transcriptions_count = 1

    while transcription_it:hasNext() do
        local transcription = transcription_it:next()
        local index_id = transcription:getReference():getTypeIndexID()
        if index_id == id then
            local t = {
                startTime = transcription:getStartTime(),
                endTime = transcription:getEndTime(),
                speaker = transcription:getSpeaker(),
                utterance = transcription:getUtterance(),
                model = transcription:getModel(),
                audio_wav_id = index_id
            }
            transcriptions[transcriptions_count] = t
            transcriptions_count = transcriptions_count + 1
        end
    end

    return transcriptions

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

    if results["modification_meta"] ~= nil and results["rttms"] ~= nil and results["transcripts"] ~= nil then
        for j, modification_meta in ipairs(results["modification_meta"]) do
            local modification_anno = luajava.newInstance("org.texttechnologylab.annotation.DocumentModification", inputCas)
            modification_anno:setUser(modification_meta["user"])
            modification_anno:setTimestamp(modification_meta["timestamp"])
            modification_anno:setComment(modification_meta["comment"])

            modification_anno:addToIndexes()
        end

        for j, rttm in ipairs(results["rttms"]) do
            local rttm_anno = luajava.newInstance("org.texttechnologylab.annotation.RTTM", inputCas)
            rttm_anno:setBegin(rttm["begin"])
            rttm_anno:setEnd(rttm["end"])
            rttm_anno:setSegmentType(rttm["segmentType"])
            rttm_anno:setChannel(rttm["channel"])
            rttm_anno:setTurnOnset(rttm["turnOnset"])
            rttm_anno:setTurnDuration(rttm["turnDuration"])
            rttm_anno:setOrthographyField(rttm["orthographyField"])
            rttm_anno:setSpeakerType(rttm["speakerType"])
            rttm_anno:setConfidenceScore(rttm["confidenceScore"])
            rttm_anno:setSignalLookaheadTime(rttm["signalLookaheadTime"])
            rttm_anno:setModel(rttm["model"])
            rttm_anno:setReference(find_audio_by_id(inputCas, rttm["audio_wav_id"]))
            rttm_anno:addToIndexes()
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
