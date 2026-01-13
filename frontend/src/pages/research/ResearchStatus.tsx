import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Loader2, CheckCircle, AlertCircle, Youtube } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress"; // Need to create
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"; // Need to create

export default function ResearchStatus() {
    const { id } = useParams();

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
                        <p className="text-green-600 font-medium">Research completed successfully.</p>
                    )}
                    {isFailed && (
                        <p className="text-red-600 font-medium">Research failed. Please try again.</p>
                    )}
                </CardContent>
            </Card>

            {/* Results View */}
            {results && (
                <div className="space-y-6">
                    <Tabs defaultValue="summary">
                        <TabsList>
                            <TabsTrigger value="summary">Analysis Summary</TabsTrigger>
                            <TabsTrigger value="sources">Sources ({results.total_sources})</TabsTrigger>
                            {results.generated_script && <TabsTrigger value="script">YouTube Script</TabsTrigger>}
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
