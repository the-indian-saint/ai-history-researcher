import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Link } from "react-router-dom";
import { Plus, Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useState } from "react";

export default function ResearchList() {
    const [search, setSearch] = useState("");

    const { data: queries, isLoading } = useQuery({
        queryKey: ["research-queries"],
        queryFn: async () => {
            const res = await axios.get("/api/v1/research/?limit=50");
            return res.data;
        }
    });

    const filteredQueries = queries?.filter((q: any) =>
        q.query.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Research History</h1>
                    <p className="text-muted-foreground">Manage and review your historical investigations.</p>
                </div>
                <Button asChild>
                    <Link to="/research/new">
                        <Plus className="mr-2 h-4 w-4" /> New Research
                    </Link>
                </Button>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Filter queries..."
                    className="pl-9"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>

            {isLoading ? (
                <div className="flex justify-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            ) : (
                <div className="grid gap-4">
                    {filteredQueries?.length === 0 ? (
                        <div className="text-center py-12 border rounded-lg bg-muted/10">
                            <p className="text-muted-foreground">No research queries found.</p>
                        </div>
                    ) : (
                        filteredQueries?.map((query: any) => (
                            <Link key={query.id} to={`/research/${query.id}/results`}>
                                <Card className="hover:bg-muted/50 transition-colors">
                                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                                        <CardTitle className="text-lg font-medium leading-none truncate pr-4">
                                            {query.query}
                                        </CardTitle>
                                        <div className={cn(
                                            "px-2.5 py-0.5 rounded-full text-xs font-semibold",
                                            query.status === 'completed' ? "bg-green-100 text-green-700" :
                                                query.status === 'processing' ? "bg-blue-100 text-blue-700" :
                                                    "bg-gray-100 text-gray-700"
                                        )}>
                                            {query.status}
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex justify-between text-sm text-muted-foreground">
                                            <span>{query.sources_found || 0} sources found</span>
                                            <span>{new Date(query.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </CardContent>
                                </Card>
                            </Link>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
