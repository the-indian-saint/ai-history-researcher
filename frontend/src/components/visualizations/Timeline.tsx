import { motion } from "framer-motion";
import { Calendar, Crown, Swords, Landmark } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export interface TimelineEvent {
    date: string;
    description: string;
    type: "event" | "reign" | "battle" | "cultural";
    significance?: string;
}

interface TimelineProps {
    events: TimelineEvent[];
}

const getEventIcon = (type: string) => {
    switch (type) {
        case "reign": return <Crown className="h-4 w-4" />;
        case "battle": return <Swords className="h-4 w-4" />;
        case "cultural": return <Landmark className="h-4 w-4" />;
        default: return <Calendar className="h-4 w-4" />;
    }
};

const getEventColor = (type: string) => {
    switch (type) {
        case "reign": return "bg-yellow-500";
        case "battle": return "bg-red-500";
        case "cultural": return "bg-purple-500";
        default: return "bg-blue-500";
    }
};

export function Timeline({ events }: TimelineProps) {
    if (!events || events.length === 0) {
        return <div className="text-center text-muted-foreground py-10">No chronological events found.</div>;
    }

    // Sort events by date if possible (basic string comparison or parse years)
    // For ancient history, dates are tricky (e.g. 320 BCE vs 320 CE). 
    // Assuming API returns sorted or we display as provided for now.

    return (
        <div className="relative border-l-2 border-primary/20 ml-4 md:ml-10 space-y-8 py-4">
            {events.map((event, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="relative pl-8 md:pl-12"
                >
                    {/* Timestamp Dot */}
                    <div className={cn(
                        "absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-background ring-4 ring-background/50",
                        getEventColor(event.type)
                    )} />

                    <Card className="hover:shadow-md transition-shadow cursor-pointer border-primary/10">
                        <CardHeader className="py-3 px-4 pb-2">
                            <div className="flex justify-between items-start">
                                <Badge variant="outline" className="mb-2 font-mono text-xs flex items-center gap-1">
                                    {getEventIcon(event.type)}
                                    {event.date}
                                </Badge>
                                <Badge className={cn("text-[10px] capitalize", getEventColor(event.type))}>
                                    {event.type}
                                </Badge>
                            </div>
                            <CardTitle className="text-base font-heading leading-tight">
                                {event.description}
                            </CardTitle>
                        </CardHeader>
                        {event.significance && (
                            <CardContent className="py-2 px-4 text-sm text-muted-foreground bg-muted/20">
                                {event.significance}
                            </CardContent>
                        )}
                    </Card>
                </motion.div>
            ))}
        </div>
    );
}
