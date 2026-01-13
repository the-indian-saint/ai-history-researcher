import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { Loader2, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label"; // Check if needs creation
import { Textarea } from "@/components/ui/textarea"; // Check if needs creation
import { Switch } from "@/components/ui/switch";

export default function NewResearch() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        query: "",
        time_period_start: "",
        time_period_end: "",
        geographical_region: "",
        generate_script: false
    });

    const mutation = useMutation({
        mutationFn: async (data: any) => {
            const res = await axios.post("/api/v1/research/", data);
            return res.data;
        },
        onSuccess: (data) => {
            navigate(`/research/${data.research_id}/status`);
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate(formData);
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm" asChild>
                    <Link to="/research"><ArrowLeft className="h-4 w-4 mr-2" /> Back</Link>
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>New Research Query</CardTitle>
                    <CardDescription>Initiate a deep dive into historical topics.</CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="query">Research Question</Label>
                            <Textarea
                                id="query"
                                placeholder="e.g., What were the economic impacts of the Gupta Empire?"
                                required
                                className="min-h-[100px]"
                                value={formData.query}
                                onChange={(e) => setFormData({ ...formData, query: e.target.value })}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="start">Time Period Start</Label>
                                <Input
                                    id="start"
                                    placeholder="e.g., 320 CE"
                                    value={formData.time_period_start}
                                    onChange={(e) => setFormData({ ...formData, time_period_start: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="end">Time Period End</Label>
                                <Input
                                    id="end"
                                    placeholder="e.g., 550 CE"
                                    value={formData.time_period_end}
                                    onChange={(e) => setFormData({ ...formData, time_period_end: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="region">Geographical Region</Label>
                            <Input
                                id="region"
                                placeholder="e.g., Ancient India"
                                value={formData.geographical_region}
                                onChange={(e) => setFormData({ ...formData, geographical_region: e.target.value })}
                            />
                        </div>

                        <div className="flex items-center space-x-2 pt-2">
                            <Switch
                                id="script"
                                checked={formData.generate_script}
                                onCheckedChange={(checked) => setFormData({ ...formData, generate_script: checked })}
                            />
                            <Label htmlFor="script">Generate YouTube Script</Label>
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button type="submit" className="w-full" disabled={mutation.isPending}>
                            {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Start Research
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
