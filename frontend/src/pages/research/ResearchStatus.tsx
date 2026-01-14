import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Loader2, CheckCircle, AlertCircle, Youtube, Image as ImageIcon, Volume2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Timeline } from "@/components/visualizations/Timeline";
import { HistoricalMap } from "@/components/visualizations/HistoricalMap";

export default function ResearchStatus() {
    const { id } = useParams();
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
    const [isGeneratingImage, setIsGeneratingImage] = useState(false);

    // Poll for status
    const { data: status, isLoading: isStatusLoading } = useQuery({
        queryKey: ["research-status", id],
        queryFn: async () => {
            const res = await axios.get(`/api/v1/research/${id}/status`);
            return res.data;
        },
        refetchInterval: (query) => {
            const data = query.state.data;
            return (data?.status === "completed" || data?.status === "failed" ? false : 2000);
        },
    });

    // Fetch results only if completed
    const { data: results } = useQuery({
        queryKey: ["research-results", id],
        queryFn: async () => {
            const res = await axios.get(`/api/v1/research/${id}/results`);
            return res.data;
        },
        enabled: status?.status === "completed",
    });

    const handleGenerateAudio = async () => {
        if (!results) return;
        setIsGeneratingAudio(true);
        try {
            const text = `Research complete for ${results.query}. Found ${results.total_sources} sources. ${JSON.stringify(results.analysis_summary)}`;
            const res = await axios.post("/api/v1/generate/audio", { text });
            setAudioUrl(res.data.url);
        } catch (e) {
            console.error("Audio generation failed", e);
        } finally {
            setIsGeneratingAudio(false);
        }
    };

    const handleGenerateImage = async () => {
        if (!results) return;
        setIsGeneratingImage(true);
        try {
            const res = await axios.post("/api/v1/generate/image", { prompt: `Historical illustration of ${results.query} in ancient India style` });
            setImageUrl(res.data.url);
        } catch (e) {
            console.error("Image generation failed", e);
        } finally {
            setIsGeneratingImage(false);
        }
    };

    if (isStatusLoading || !status) {
        return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    }

    const isCompleted = status.status === "completed";
    const isFailed = status.status === "failed";
    const progress = Math.round(status.progress * 100);

    return (
        <div className="space-y-6">
            {/* Status Header */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <CardTitle className="text-xl">Research Status: {status.status}</CardTitle>
                            <p className="text-sm text-muted-foreground">ID: {id}</p>
                        </div>
                        {isCompleted ? (
                            <CheckCircle className="h-8 w-8 text-green-500" />
                        ) : isFailed ? (
                            <AlertCircle className="h-8 w-8 text-red-500" />
                        ) : (
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        )}
                    </div>
                </CardHeader>
                <CardContent>
                    {!isCompleted && !isFailed && (
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span>Progress</span>
                                <span>{progress}%</span>
                            </div>
                            <Progress value={progress} />
                            <p className="text-sm text-muted-foreground animate-pulse text-center pt-2">
                                Analyzing documents and extracting insights...
                            </p>
                        </div>
                    )}
                    {isCompleted && (
                        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                            <p className="text-green-600 font-medium">Research completed successfully.</p>
                            <div className="flex gap-2">
                                <Button variant="outline" size="sm" onClick={handleGenerateAudio} disabled={isGeneratingAudio}>
                                    {isGeneratingAudio ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Volume2 className="h-4 w-4 mr-2" />}
                                    {audioUrl ? "Regenerate Audio" : "Listen to Summary"}
                                </Button>
                                <Button variant="outline" size="sm" onClick={handleGenerateImage} disabled={isGeneratingImage}>
                                    {isGeneratingImage ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <ImageIcon className="h-4 w-4 mr-2" />}
                                    {imageUrl ? "Regenerate Image" : "Generate Illustration"}
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* Media Players */}
                    {isCompleted && (
                        <div className="mt-4 grid gap-4 md:grid-cols-2">
                            {audioUrl && (
                                <div className="bg-muted p-2 rounded-md flex items-center gap-2 animate-in fade-in">
                                    <Volume2 className="h-4 w-4" />
                                    <audio controls src={audioUrl} className="w-full h-8" />
                                </div>
                            )}
                            {imageUrl && (
                                <div className="border rounded-md overflow-hidden animate-in fade-in">
                                    <img src={imageUrl} alt="Generated Historical Illustration" className="w-full h-48 object-cover" />
                                </div>
                            )}
                        </div>
                    )}

                    {isFailed && (
                        <p className="text-red-600 font-medium">Research failed. Please try again.</p>
                    )}
                </CardContent>
            </Card>

            {/* Results View */}
            {results && (
                <div className="space-y-6">
                    <Tabs defaultValue="summary" className="w-full">
                        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5">
                            <TabsTrigger value="summary">Summary</TabsTrigger>
                            <TabsTrigger value="timeline">Timeline</TabsTrigger>
                            <TabsTrigger value="map">Map</TabsTrigger>
                            <TabsTrigger value="sources">Sources ({results.total_sources})</TabsTrigger>
                            <TabsTrigger value="script" disabled={!results.generated_script}>Script</TabsTrigger>
                        </TabsList>

                        <TabsContent value="summary" className="space-y-4">
                            <Card>
                                <CardHeader><CardTitle>Key Findings</CardTitle></CardHeader>
                                <CardContent>
                                    <div className="prose dark:prose-invert max-w-none">
                                        <pre className="whitespace-pre-wrap font-sans text-sm">
                                            {JSON.stringify(results.analysis_summary, null, 2)}
                                        </pre>
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        <TabsContent value="timeline" className="space-y-4">
                            <Card>
                                <CardHeader><CardTitle>Historical Timeline</CardTitle></CardHeader>
                                <CardContent>
                                    <Timeline events={results.timeline_events || []} />
                                </CardContent>
                            </Card>
                        </TabsContent>

                        <TabsContent value="map" className="space-y-4">
                            <Card>
                                <CardHeader><CardTitle>Geographic Context</CardTitle></CardHeader>
                                <CardContent className="p-0 overflow-hidden">
                                    <HistoricalMap locations={results.locations || []} />
                                </CardContent>
                            </Card>
                        </TabsContent>

                        <TabsContent value="sources" className="space-y-4">
                            <div className="grid gap-4 md:grid-cols-2">
                                {results.sources.map((source: any, i: number) => (
                                    <Card key={i}>
                                        <CardHeader>
                                            <CardTitle className="text-base truncate">{source.title}</CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-2">
                                            <p className="text-sm text-muted-foreground line-clamp-3">{source.snippet || "No snippet available."}</p>
                                            <div className="flex justify-end">
                                                <Button variant="outline" size="sm" asChild>
                                                    <a href={source.source_url} target="_blank" rel="noopener noreferrer">View Source</a>
                                                </Button>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </TabsContent>

                        {results.generated_script && (
                            <TabsContent value="script">
                                <Card>
                                    <CardHeader className="flex flex-row items-center space-x-2">
                                        <Youtube className="h-6 w-6 text-red-600" />
                                        <CardTitle>Generated Script</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded-md">
                                            {results.generated_script.script || "Script generation failed."}
                                        </div>
                                    </CardContent>
                                </Card>
                            </TabsContent>
                        )}
                    </Tabs>
                </div>
            )}
        </div>
    );
}
