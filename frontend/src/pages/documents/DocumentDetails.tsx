import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { Loader2, ArrowLeft, Trash2, Calendar, User, Globe, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Link } from "react-router-dom";

export default function DocumentDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { data: document, isLoading } = useQuery({
        queryKey: ["document", id],
        queryFn: async () => {
            const res = await axios.get(`/api/v1/documents/${id}`);
            return res.data;
        }
    });

    const { data: analysisHistory } = useQuery({
        queryKey: ["analysis-history", id],
        queryFn: async () => {
            const res = await axios.get(`/api/v1/analysis/history/${id}`);
            return res.data;
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async () => {
            await axios.delete(`/api/v1/documents/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            navigate("/documents");
        }
    });

    if (isLoading || !document) {
        return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <Button variant="ghost" size="sm" asChild>
                    <Link to="/documents"><ArrowLeft className="h-4 w-4 mr-2" /> Back to Library</Link>
                </Button>
                <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate()}>
                    <Trash2 className="h-4 w-4 mr-2" /> Delete Document
                </Button>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                {/* Sidebar Info */}
                <Card className="md:col-span-1 h-fit">
                    <CardHeader>
                        <CardTitle className="text-lg">Metadata</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm">
                        <div className="flex items-center justify-between">
                            <span className="text-muted-foreground">Type</span>
                            <Badge variant="outline">{document.source_type}</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-muted-foreground flex items-center"><User className="h-3 w-3 mr-1" /> Author</span>
                            <span className="truncate max-w-[150px]">{document.author || "Unknown"}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-muted-foreground flex items-center"><Calendar className="h-3 w-3 mr-1" /> Date</span>
                            <span>{new Date(document.created_at).toLocaleDateString()}</span>
                        </div>
                        {document.source_url && (
                            <div className="pt-2">
                                <Button variant="outline" size="sm" className="w-full" asChild>
                                    <a href={document.source_url} target="_blank" rel="noopener noreferrer">
                                        <Globe className="h-3 w-3 mr-2" /> Open Source
                                    </a>
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Main Content */}
                <div className="md:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-2xl">{document.title}</CardTitle>
                            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                                <span>{document.word_count || 0} words</span>
                                <span>•</span>
                                <span>{document.language}</span>
                                <span>•</span>
                                <span className={document.credibility_score > 0.7 ? "text-green-500" : "text-yellow-500"}>
                                    {Math.round((document.credibility_score || 0) * 100)}% Credibility
                                </span>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <h3 className="text-sm font-semibold mb-2">Summary</h3>
                            <p className="text-muted-foreground leading-relaxed">
                                {document.content_summary || "No summary available."}
                            </p>
                        </CardContent>
                    </Card>

                    <Tabs defaultValue="analysis">
                        <TabsList>
                            <TabsTrigger value="analysis">Analysis History</TabsTrigger>
                            <TabsTrigger value="raw">Raw Content</TabsTrigger>
                        </TabsList>
                        <TabsContent value="analysis">
                            <Card>
                                <CardHeader><CardTitle>Past Analyses</CardTitle></CardHeader>
                                <CardContent>
                                    {analysisHistory?.analyses?.length > 0 ? (
                                        <div className="space-y-4">
                                            {analysisHistory.analyses.map((analysis: any) => (
                                                <div key={analysis.id} className="border-b pb-4 last:border-0">
                                                    <div className="flex justify-between mb-2">
                                                        <span className="font-semibold capitalize">{analysis.analysis_type}</span>
                                                        <span className="text-xs text-muted-foreground">{new Date(analysis.created_at).toLocaleDateString()}</span>
                                                    </div>
                                                    <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-40">
                                                        {JSON.stringify(analysis.result, null, 2)}
                                                    </pre>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-8 text-muted-foreground">
                                            <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
                                            No analysis history found.
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </TabsContent>
                        <TabsContent value="raw">
                            <Card>
                                <CardContent className="pt-6">
                                    <p className="text-muted-foreground italic">Raw content viewing not fully implemented. See summary.</p>
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
