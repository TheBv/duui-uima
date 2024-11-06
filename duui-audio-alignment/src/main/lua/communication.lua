StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")
Class = luajava.bindClass("java.lang.Class")
JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
DUUIUtils = luajava.bindClass("org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaUtils")
AudioWav = luajava.bindClass("org.texttechnologylab.annotation.AudioWav")
Transcription = luajava.bindClass("org.texttechnologylab.annotation.Transcription")
RTTM = luajava.bindClass("org.texttechnologylab.annotation.RTTM")

function serialize(inputCas, outputStream, parameters)
    local doc_lang = inputCas:getDocumentLanguage()

    local use_punct = parameters["use_punct"] or false

    local align = {}
    local align_count = 1

    local audio_it = JCasUtil:select(inputCas, AudioWav):iterator()

    while audio_it:hasNext() do
        local audio = audio_it:next()



        align[align_count] = {
            rttms = find_rttms_by_id(inputCas, audio:getTypeIndexID()),
            transcriptions = find_transcriptions_by_id(inputCas, audio:getTypeIndexID())
        }
        align_count = align_count + 1
    end

    
    outputStream:write(json.encode({
        align = align,
        lang = doc_lang,
        use_punct = use_punct
    }))
end


function find_rttms_by_id(inputCas, id)
    local rttm_it = JCasUtil:select(inputCas, RTTM):iterator()

    local rttms = {}
    local rttms_count = 1

    while rttm_it:hasNext() do
        local rttm = rttm_it:next()
        local index_id = rttm:getReference():getTypeIndexID()
        if index_id == id then
            local r = {
                segmentType = rttm:getSegmentType(),
                channel = rttm:getChannel(),
                turnOnset = rttm:getTurnOnset(),
                turnDuration = rttm:getTurnDuration(),
                orthographyField = rttm:getOrthographyField(),
                speakerType = rttm:getSpeakerType(),
                speakerName = rttm:getSpeakerName(),
                confidenceScore = rttm:getConfidenceScore(),
                signalLookaheadTime = rttm:getSignalLookaheadTime(),
                model = rttm:getModel(),
                audio_wav_id = index_id
            }
            rttms[rttms_count] = r
            rttms_count = rttms_count + 1
        end
    end

    return rttms

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

    if results["modification_meta"] ~= nil and results["transcriptions"] ~= nil then
        for j, modification_meta in ipairs(results["modification_meta"]) do
            local modification_anno = luajava.newInstance("org.texttechnologylab.annotation.DocumentModification", inputCas)
            modification_anno:setUser(modification_meta["user"])
            modification_anno:setTimestamp(modification_meta["timestamp"])
            modification_anno:setComment(modification_meta["comment"])

            modification_anno:addToIndexes()
        end

        for j, transcription in ipairs(results["transcriptions"]) do
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
