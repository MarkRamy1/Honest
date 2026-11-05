import React from 'react';
import {
  ArrowRight,
  ArrowUpRight,
  ArrowUp,
  Bookmark,
  Check,
  ChevronRight,
  CircleHelp,
  Clock3,
  Download,
  ExternalLink,
  Headphones,
  Heart,
  Home,
  Link,
  LoaderCircle,
  LogOut,
  Menu,
  MessageCircle,
  Plus,
  Search,
  Send,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Star,
  ScanLine,
  Trash2,
  Users,
  X,
  Scale,
  ShoppingBag,
  Copy,
  CheckCircle2,
  AlertCircle,
  Sun,
  Moon
} from 'lucide-react';

const icons = {
  arrow: ArrowRight,
  diagonal: ArrowUpRight,
  up: ArrowUp,
  bookmark: Bookmark,
  check: Check,
  chevron: ChevronRight,
  help: CircleHelp,
  clock: Clock3,
  download: Download,
  external: ExternalLink,
  headphones: Headphones,
  heart: Heart,
  home: Home,
  link: Link,
  loading: LoaderCircle,
  logout: LogOut,
  menu: Menu,
  chat: MessageCircle,
  plus: Plus,
  search: Search,
  send: Send,
  settings: Settings,
  shield: ShieldCheck,
  sliders: SlidersHorizontal,
  sparkles: Sparkles,
  star: Star,
  scan: ScanLine,
  trash: Trash2,
  users: Users,
  close: X,
  scale: Scale,
  bag: ShoppingBag,
  copy: Copy,
  success: CheckCircle2,
  alert: AlertCircle,
  sun: Sun,
  moon: Moon
};

export interface IconProps {
  readonly name: string;
  readonly size?: number;
  readonly className?: string;
}

export function Icon({ name, size = 20, className }: Readonly<IconProps>) {
  const Component = icons[name as keyof typeof icons] || Sparkles;
  return <Component size={size} strokeWidth={1.75} className={className} aria-hidden="true" />;
}
