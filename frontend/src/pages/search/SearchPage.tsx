import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Search, Filter, Loader2, Calendar, User, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

export default function SearchPage() {
    const [filters, setFilters] = useState({
        q: "",
        title: "",
        author: "",
        source_type: "all",
        language: "all",
        min_credibility: 0
    });

    // De-bounce or manual trigger could be better, but for now we search on button click
    const [activeSearch, setActiveSearch] = useState(false);

    const { data: searchResults, isLoading, refetch } = useQuery({
        queryKey: ["advanced-search", filters],
        queryFn: async () => {
            const params = new URLSearchParams();
            if (filters.q) params.append("q", filters.q);
            if (filters.title) params.append("title", filters.title);
            if (filters.author) params.append("author", filters.author);
            if (filters.source_type !== "all") params.append("source_type", filters.source_type);
            if (filters.language !== "all") params.append("language", filters.language);
            if (filters.min_credibility > 0) params.append("min_credibility", (filters.min_credibility / 100).toString());

            // Initial load shouldn't fire if empty, but we'll let it or handle "activeSearch"
            if (!activeSearch) return { results: [], count: 0 };

            const res = await axios.get(`/api/v1/search/advanced?${params.toString()}`);
            return res.data;
        },
        enabled: activeSearch
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setActiveSearch(true);
        refetch();
    };

    return (
        <div className="grid gap-6 md:grid-cols-4 lg:grid-cols-5">
            {/* Sidebar Filters */}
            <div className="md:col-span-1 space-y-6">
                <div className="flex items-center space-x-2">
                    <Filter className="h-5 w-5" />
                    <h2 className="text-lg font-semibold">Filters</h2>
                </div>

                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="author">Author</Label>
                        <Input
                            id="author"
                            placeholder="e.g. Herodotus"
                            value={filters.author}
                            onChange={(e) => setFilters({ ...filters, author: e.target.value })}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label>Source Type</Label>
                        <Select
                            value={filters.source_type}
                            onValueChange={(val) => setFilters({ ...filters, source_type: val })}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="All Types" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Types</SelectItem>
                                <SelectItem value="academic">Academic</SelectItem>
                                <SelectItem value="primary">Primary Source</SelectItem>
                                <SelectItem value="web">Web</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label>Language</Label>
                        <Select
                            value={filters.language}
                            onValueChange={(val) => setFilters({ ...filters, language: val })}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="All Languages" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Languages</SelectItem>
                                <SelectItem value="english">English</SelectItem>
                                <SelectItem value="sanskrit">Sanskrit</SelectItem>
                                <SelectItem value="greek">Greek</SelectItem>
                                <SelectItem value="latin">Latin</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-3 pt-2">
                        <div className="flex justify-between">
                            <Label>Min Credibility</Label>
                            <span className="text-xs text-muted-foreground">{filters.min_credibility}%</span>
                        </div>
                        <Slider
                            value={[filters.min_credibility]}
                            max={100}
                            step={5}
                            onValueChange={(val) => setFilters({ ...filters, min_credibility: val[0] })}
                        />
                    </div>
                </form>
            </div>

            {/* Main Search Area */}
            <div className="md:col-span-3 lg:col-span-4 space-y-6">
                <form onSubmit={handleSearch} className="flex gap-2">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search with keywords, title, or summary..."
                            className="pl-9 h-10"
                            value={filters.q}
                            onChange={(e) => setFilters({ ...filters, q: e.target.value })}
                        />
                    </div>
                    <Button type="submit" size="default">
                        Search
                    </Button>
                </form>

                {/* Results */}
                <div className="space-y-4">
                    {isLoading ? (
                        <div className="flex justify-center py-12">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        searchResults?.results?.length === 0 ? (
                            <div className="text-center py-12 text-muted-foreground bg-muted/20 rounded-lg border-2 border-dashed">
                                {activeSearch ? "No results found matching your criteria." : "Enter a term or apply filters to start searching."}
                            </div>
                        ) : (
                            searchResults?.results.map((result: any) => (
                                <Card key={result.id} className="hover:border-primary/50 transition-colors">
                                    <CardHeader className="pb-2">
                                        <div className="flex justify-between items-start">
                                            <div className="space-y-1">
                                                <CardTitle className="text-lg">
                                                    <a href={result.source_url || "#"} className="hover:underline flex items-center gap-2">
                                                        {result.title}
                                                        {result.source_url && <ExternalLink className="h-3 w-3 opacity-50" />}
                                                    </a>
                                                </CardTitle>
                                                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                                    {result.author && <span className="flex items-center"><User className="h-3 w-3 mr-1" /> {result.author}</span>}
                                                    <span className="flex items-center"><Calendar className="h-3 w-3 mr-1" /> {new Date(result.created_at).getFullYear()}</span>
                                                </div>
                                            </div>
                                            <Badge variant={result.credibility_score > 0.7 ? "default" : "secondary"}>
                                                {Math.round(result.credibility_score * 100)}% Trusted
                                            </Badge>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <p className="text-sm text-muted-foreground line-clamp-2">
                                            {result.summary || "No summary available."}
                                        </p>
                                    </CardContent>
                                    <CardFooter className="pt-0 pb-4">
                                        <div className="flex gap-2 text-xs">
                                            <Badge variant="outline" className="capitalize">{result.source_type}</Badge>
                                            <Badge variant="outline" className="capitalize">{result.language}</Badge>
                                        </div>
                                    </CardFooter>
                                </Card>
                            ))
                        )
                    )}
                </div>
            </div>
        </div>
    );
}
