import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Search, FileText, Activity, AlertCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export default function Dashboard() {
    const { data: health } = useQuery({
        queryKey: ["health"],
        queryFn: async () => {
            const res = await axios.get("/health/");
            return res.data;
        }
    });

    const { data: recentResearch } = useQuery({
        queryKey: ["recentResearch"],
        queryFn: async () => {
            const res = await axios.get("/api/v1/research/?limit=5");
            return res.data;
        }
    });

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <section className="text-center space-y-6 py-16 md:py-24">
                <h1 className="text-4xl md:text-6xl font-heading font-bold tracking-tight text-primary drop-shadow-sm">
                    Uncover the Past with AI
                </h1>
                <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto font-serif leading-relaxed">
                    Advanced automated research for ancient history using multi-agent AI, semantic search, and document analysis.
                </p>

                <div className="max-w-xl mx-auto relative pt-4">
                    <Input
                        placeholder="Quick search documents..."
                        className="h-14 pl-12 rounded-full shadow-lg border-primary/20 bg-background/80 backdrop-blur-sm text-lg"
                    />
                    <Search className="absolute left-5 top-8 h-6 w-6 text-muted-foreground" />
                </div>
            </section>

            {/* Stats / Quick Actions */}
            <div className="grid gap-6 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">System Status</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {health?.status === "healthy" ? (
                                <span className="text-green-500">Healthy</span>
                            ) : (
                                <span className="text-yellow-500">{health?.status || "Unknown"}</span>
                            )}
                        </div>
                        <p className="text-xs text-muted-foreground">Version: {health?.version || "0.0.0"}</p>
                    </CardContent>
                </Card>

                <Card className="hover:bg-muted/50 transition-colors cursor-pointer group">
                    <Link to="/research">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">New Research</CardTitle>
                            <Search className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">Start Now</div>
                            <p className="text-xs text-muted-foreground">Launch a new investigation</p>
                        </CardContent>
                    </Link>
                </Card>

                <Card className="hover:bg-muted/50 transition-colors cursor-pointer group">
                    <Link to="/documents">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Upload Docs</CardTitle>
                            <FileText className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">Add Source</div>
                            <p className="text-xs text-muted-foreground">PDF, Text, or URL</p>
                        </CardContent>
                    </Link>
                </Card>
            </div>

            {/* Recent Activity */}
            <Card>
                <CardHeader>
                    <CardTitle>Recent Research</CardTitle>
                    <CardDescription>Your latest historical inquiries and their status.</CardDescription>
                </CardHeader>
                <CardContent>
                    {recentResearch && recentResearch.length > 0 ? (
                        <div className="space-y-4">
                            {recentResearch.map((item: any) => (
                                <div key={item.id} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                                    <div className="space-y-1">
                                        <p className="font-medium leading-none truncate max-w-[300px]">{item.query}</p>
                                        <p className="text-sm text-muted-foreground">{new Date(item.created_at).toLocaleDateString()}</p>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className={cn(
                                            "px-2 py-1 rounded-full text-xs font-medium",
                                            item.status === 'completed' ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
                                                item.status === 'processing' ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" :
                                                    "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
                                        )}>
                                            {item.status}
                                        </span>
                                        <Button variant="ghost" size="sm" asChild>
                                            <Link to={`/research/${item.id}/results`}>View</Link>
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
                            <AlertCircle className="h-8 w-8 mb-2" />
                            <p>No research history found.</p>
                            <Button variant="link" asChild className="mt-2">
                                <Link to="/research">Start your first research query</Link>
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
