import { Link, Outlet, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Search,
    BookOpen,
    FileText,
    Menu,
    History
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const SidebarItem = ({
    icon: Icon,
    label,
    to,
    active,
    onClick
}: {
    icon: any;
    label: string;
    to: string;
    active: boolean;
    onClick?: () => void;
}) => (
    <Link
        to={to}
        onClick={onClick}
        className={cn(
            "flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors",
            active
                ? "bg-primary/10 text-primary font-medium"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
        )}
    >
        <Icon className="h-5 w-5" />
        <span>{label}</span>
    </Link>
);

export default function MainLayout() {
    const location = useLocation();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const navItems = [
        { icon: LayoutDashboard, label: "Dashboard", to: "/" },
        { icon: Search, label: "Research", to: "/research" },
        { icon: FileText, label: "Documents", to: "/documents" },
        { icon: BookOpen, label: "Advanced Search", to: "/search" },
        // { icon: Video, label: "Studio", to: "/studio" }, // Future
    ];

    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Mobile Menu Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={cn(
                    "fixed lg:static inset-y-0 left-0 z-50 w-72 border-r bg-card shadow-sm transform transition-transform duration-200 lg:transform-none",
                    isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="h-16 flex items-center px-6 border-b">
                    <History className="h-6 w-6 text-primary mr-2" />
                    <span className="text-xl font-heading font-bold tracking-wide">AI Historian</span>
                </div>

                <nav className="p-4 space-y-2">
                    {navItems.map((item) => (
                        <SidebarItem
                            key={item.to}
                            icon={item.icon}
                            label={item.label}
                            to={item.to}
                            active={location.pathname === item.to || (item.to !== "/" && location.pathname.startsWith(item.to))}
                            onClick={() => setIsMobileMenuOpen(false)}
                        />
                    ))}
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-background/50">
                {/* Mobile Header */}
                <header className="lg:hidden h-16 border-b flex items-center px-4 bg-card">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setIsMobileMenuOpen(true)}
                    >
                        <Menu className="h-6 w-6" />
                    </Button>
                    <span className="ml-4 font-heading font-semibold text-lg">AI Historian</span>
                </header>

                {/* Page Content */}
                <div className="flex-1 overflow-auto p-4 md:p-8">
                    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
                        <Outlet />
                    </div>
                </div>
            </main>
        </div>
    );
}
