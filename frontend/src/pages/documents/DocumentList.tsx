import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { Link } from "react-router-dom";
import { Plus, Link as LinkIcon, FileText, Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

export default function DocumentList() {
    const queryClient = useQueryClient();
    const [search, setSearch] = useState("");
    const [filterSource, setFilterSource] = useState<string>("all");
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [isUrlOpen, setIsUrlOpen] = useState(false);

    // Upload State
    const [file, setFile] = useState<File | null>(null);
    const [url, setUrl] = useState("");
    const [uploadTitle, setUploadTitle] = useState("");

    const { data: result, isLoading } = useQuery({
        queryKey: ["documents", filterSource],
        queryFn: async () => {
            const params = new URLSearchParams();
            params.append("limit", "50");
            if (filterSource !== "all") params.append("source_type", filterSource);
            const res = await axios.get(`/api/v1/documents/?${params.toString()}`);
            return res.data;
        }
    });

    const uploadMutation = useMutation({
        mutationFn: async (formData: FormData) => {
            const res = await axios.post("/api/v1/documents/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            return res.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            setIsUploadOpen(false);
            setFile(null);
            setUploadTitle("");
        }
    });

    const urlMutation = useMutation({
        mutationFn: async (data: { url: string; title: string }) => {
            const res = await axios.post(`/api/v1/documents/url?url=${encodeURIComponent(data.url)}`, {
                title: data.title,
                source_type: "web"
            });
            return res.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            setIsUrlOpen(false);
            setUrl("");
            setUploadTitle("");
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: string) => {
            await axios.delete(`/api/v1/documents/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["documents"] });
        }
    });

    const handleUpload = (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);
        if (uploadTitle) formData.append("title", uploadTitle);
        uploadMutation.mutate(formData);
    };

    const handleUrlSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!url) return;
        urlMutation.mutate({ url, title: uploadTitle });
    };

    const documents = result?.documents || [];
    const filteredDocs = documents.filter((doc: any) =>
        doc.title.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Document Library</h1>
                    <p className="text-muted-foreground">Manage your source materials and knowledge base.</p>
                </div>
                <div className="flex gap-2">
                    <Dialog open={isUrlOpen} onOpenChange={setIsUrlOpen}>
                        <DialogTrigger asChild>
                            <Button variant="outline">
                                <LinkIcon className="mr-2 h-4 w-4" /> Add URL
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Add Web Source</DialogTitle>
                                <DialogDescription>Process content from a website URL.</DialogDescription>
                            </DialogHeader>
                            <form onSubmit={handleUrlSubmit} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="url">URL</Label>
                                    <Input id="url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://..." required />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="urlTitle">Title (Optional)</Label>
                                    <Input id="urlTitle" value={uploadTitle} onChange={(e) => setUploadTitle(e.target.value)} placeholder="Custom title" />
                                </div>
                                <DialogFooter>
                                    <Button type="submit" disabled={urlMutation.isPending}>
                                        {urlMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                        Add Source
                                    </Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>

                    <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="mr-2 h-4 w-4" /> Upload File
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Upload Document</DialogTitle>
                                <DialogDescription>Supported formats: PDF, TXT, MD.</DialogDescription>
                            </DialogHeader>
                            <form onSubmit={handleUpload} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="file">File</Label>
                                    <Input id="file" type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="fileTitle">Title (Optional)</Label>
                                    <Input id="fileTitle" value={uploadTitle} onChange={(e) => setUploadTitle(e.target.value)} placeholder="Custom title" />
                                </div>
                                <DialogFooter>
                                    <Button type="submit" disabled={uploadMutation.isPending}>
                                        {uploadMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                        Upload
                                    </Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="relative flex-1">
                    <Input
                        placeholder="Search documents..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <Select value={filterSource} onValueChange={setFilterSource}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Source Type" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="academic">Academic</SelectItem>
                        <SelectItem value="web">Web</SelectItem>
                        <SelectItem value="primary">Primary Source</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {isLoading ? (
                <div className="flex justify-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filteredDocs.length === 0 ? (
                        <div className="col-span-full text-center py-12 border rounded-lg bg-muted/10">
                            <p className="text-muted-foreground">No documents found.</p>
                        </div>
                    ) : (
                        filteredDocs.map((doc: any) => (
                            <Card key={doc.id} className="group relative">
                                <CardHeader className="pb-2">
                                    <div className="flex justify-between items-start">
                                        <FileText className="h-8 w-8 text-muted-foreground mb-2" />
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-500"
                                            onClick={() => deleteMutation.mutate(doc.id)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                    <CardTitle className="text-lg leading-tight truncate" title={doc.title}>
                                        {doc.title}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="pb-2">
                                    <div className="text-xs text-muted-foreground space-y-1">
                                        <div className="flex justify-between">
                                            <span>{doc.source_type}</span>
                                            <span>{Math.round((doc.credibility_score || 0) * 100)}% Credibility</span>
                                        </div>
                                        <div>{new Date(doc.created_at).toLocaleDateString()}</div>
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button variant="secondary" className="w-full" asChild>
                                        <Link to={`/documents/${doc.id}`}>View Details</Link>
                                    </Button>
                                </CardFooter>
                            </Card>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
