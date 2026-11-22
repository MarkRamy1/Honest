import React, { useState, useEffect, Suspense, lazy } from 'react';
import { PreferencesProvider, usePreferences } from './preferences';
import { Shell } from './components/Shell';
import { AccountDialog } from './components/AccountDialog';
import { Dashboard } from './pages/Dashboard';
import { api } from './services/api';
import type { Page, Product, AnalysisRecord, ChatThread, ChatMessage, User } from './types';

// Lazy-loaded route chunks (vercel-react-best-practices: bundle-dynamic-imports)
const Analysis = lazy(() => import('./pages/Analysis').then((m) => ({ default: m.Analysis })));
const Assistant = lazy(() => import('./pages/Assistant').then((m) => ({ default: m.Assistant })));
const Saved = lazy(() => import('./pages/Saved').then((m) => ({ default: m.Saved })));
const Community = lazy(() => import('./pages/Community').then((m) => ({ default: m.Community })));
const Settings = lazy(() => import('./pages/Settings').then((m) => ({ default: m.Settings })));
const PreviewPage = lazy(() => import('./pages/PreviewPage').then((m) => ({ default: m.PreviewPage })));

function MainApp() {
  const { language } = usePreferences();
  const [page, setPage] = useState<Page>(() => {
    const hash = window.location.hash.slice(1).split('?')[0] as Page;
    const validPages: Page[] = [
      'dashboard',
      'analysis',
      'assistant',
      'saved',
      'reviews',
      'settings',
      'studio',
      'compare',
      'extension',
      'preview'
    ];
    return validPages.includes(hash) ? hash : 'dashboard';
  });

  // State: Saved products
  const [saved, setSaved] = useState<Product[]>(() => {
    try {
      const stored = localStorage.getItem('honest_saved_products');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // State: Analysis history
  const [history, setHistory] = useState<AnalysisRecord[]>(() => {
    try {
      const stored = localStorage.getItem('honest_analysis_history');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // State: Active Record & Product under analysis
  const [record, setRecord] = useState<AnalysisRecord | null>(() => {
    try {
      const stored = localStorage.getItem('honest_analysis_history');
      const list: AnalysisRecord[] = stored ? JSON.parse(stored) : [];
      return list.length > 0 ? list[0] : null;
    } catch {
      return null;
    }
  });
  const [analysisProduct, setAnalysisProduct] = useState<Product | null>(null);

  // State: User & Auth
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem('honest_auth_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [accountOpen, setAccountOpen] = useState(false);

  // State: Online Health
  const [isOnline, setIsOnline] = useState(true);

  // State: Toast message
  const [toast, setToast] = useState('');

  // State: Assistant Chat Threads
  const [threads, setThreads] = useState<ChatThread[]>(() => {
    try {
      const stored = localStorage.getItem('honest_chat_threads');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const [activeThreadId, setActiveThreadId] = useState<string | null>(() => {
    try {
      const stored = localStorage.getItem('honest_chat_threads');
      const list: ChatThread[] = stored ? JSON.parse(stored) : [];
      return list.length > 0 ? list[0].id : null;
    } catch {
      return null;
    }
  });
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatPrompt, setChatPrompt] = useState('');

  // Hash listener for navigation & extension deep-linking
  useEffect(() => {
    const processHash = () => {
      const fullHash = window.location.hash.slice(1);
      if (!fullHash) return;
      const [hashPart, queryPart] = fullHash.split('?');
      const hash = hashPart as Page;
      const validPages: Page[] = [
        'dashboard',
        'analysis',
        'assistant',
        'saved',
        'reviews',
        'settings',
        'studio',
        'compare',
        'extension',
        'preview'
      ];
      if (validPages.includes(hash)) {
        setPage(hash);
      }

      // Process query parameters from Chrome Extension or deep links
      if (queryPart) {
        const params = new URLSearchParams(queryPart);
        const productTitle = params.get('productTitle') || params.get('title');
        const price = params.get('price');
        const image = params.get('image');
        const promptParam = params.get('prompt');

        if (productTitle) {
          const incomingProduct: Product = {
            id: Date.now(),
            name: productTitle,
            original_msrp: price || '$49.99',
            image: image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80',
            url: window.location.href,
            category: 'E-Commerce Listing'
          };
          setAnalysisProduct(incomingProduct);
          setToast(language === 'ar' 
            ? `تم استيراد المنتج من إضافة المتصفح: ${productTitle.slice(0, 32)}...` 
            : `Imported product from Honest Extension: ${productTitle.slice(0, 32)}...`);
        }

        if (promptParam) {
          setChatPrompt(promptParam);
        }
      }
      window.scrollTo(0, 0);
    };

    // Process on initial mount
    processHash();

    window.addEventListener('hashchange', processHash);
    return () => window.removeEventListener('hashchange', processHash);
  }, [language]);

  // Sync state to LocalStorage
  useEffect(() => {
    localStorage.setItem('honest_saved_products', JSON.stringify(saved));
  }, [saved]);

  useEffect(() => {
    localStorage.setItem('honest_analysis_history', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    localStorage.setItem('honest_chat_threads', JSON.stringify(threads));
  }, [threads]);

  // Toast auto-dismiss
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(''), 4500);
    return () => clearTimeout(timer);
  }, [toast]);

  // Check health and user on mount in parallel (vercel-react-best-practices: async-parallel)
  useEffect(() => {
    let isMounted = true;
    Promise.allSettled([api.checkHealth(), api.getMe()]).then(([healthRes, meRes]) => {
      if (!isMounted) return;
      if (healthRes.status === 'fulfilled') {
        setIsOnline(healthRes.value.status === 'online');
      } else {
        setIsOnline(false);
      }

      if (meRes.status === 'fulfilled' && meRes.value.authenticated && meRes.value.user) {
        setUser(meRes.value.user);
        localStorage.setItem('honest_auth_user', JSON.stringify(meRes.value.user));
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const navigate = (nextPage: Page) => {
    window.location.hash = nextPage;
    setPage(nextPage);
  };

  const handleToggleSave = (product: Product) => {
    const exists = saved.some((p) => p.name === product.name);
    if (exists) {
      setSaved((prev) => prev.filter((p) => p.name !== product.name));
      setToast('Product removed from your shortlist.');
    } else {
      setSaved((prev) => [product, ...prev]);
      setToast('Product saved to your shortlist.');
    }
  };

  const handleSelectProduct = (product: Product) => {
    setAnalysisProduct(product);
    navigate('analysis');
  };

  const handleSelectRecord = (rec: AnalysisRecord) => {
    setRecord(rec);
    setAnalysisProduct(rec.product);
    navigate('analysis');
  };

  const handleRecordChange = (rec: AnalysisRecord) => {
    setRecord(rec);
    setHistory((prev) => [rec, ...prev.filter((h) => h.product.name !== rec.product.name)].slice(0, 50));
  };

  // Assistant actions
  const handleNewThread = () => {
    const newThread: ChatThread = {
      id: 'thread-' + Date.now(),
      title: language === 'ar' ? 'محادثة جديدة' : 'New Research Session',
      model: 'gemini-2.5-flash',
      createdAt: new Date().toISOString(),
      messages: []
    };
    setThreads((prev) => [newThread, ...prev]);
    setActiveThreadId(newThread.id);
  };

  const handleDeleteThread = (id: string) => {
    setThreads((prev) => prev.filter((t) => t.id !== id));
    if (activeThreadId === id) {
      const remaining = threads.filter((t) => t.id !== id);
      setActiveThreadId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const handleSendMessage = async (text: string, mode: 'detailed' | 'quick' = 'detailed', model: string = 'gemini-2.5-flash') => {
    if (isChatLoading) return;

    let targetThreadId = activeThreadId;
    let currentThreads = [...threads];

    const userMessage: ChatMessage = {
      id: 'msg-' + Date.now(),
      sender: 'user',
      role: 'user',
      text,
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    if (!targetThreadId || !currentThreads.some((t) => t.id === targetThreadId)) {
      const newThread: ChatThread = {
        id: 'thread-' + Date.now(),
        title: text.slice(0, 32) + (text.length > 32 ? '...' : ''),
        model,
        createdAt: new Date().toISOString(),
        messages: [userMessage]
      };
      currentThreads = [newThread, ...currentThreads];
      targetThreadId = newThread.id;
      setThreads(currentThreads);
      setActiveThreadId(targetThreadId);
    } else {
      currentThreads = currentThreads.map((t) => {
        if (t.id === targetThreadId) {
          const isFirst = t.messages.length === 0;
          return {
            ...t,
            title: isFirst ? text.slice(0, 32) + (text.length > 32 ? '...' : '') : t.title,
            messages: [...t.messages, userMessage]
          };
        }
        return t;
      });
      setThreads(currentThreads);
    }

    setIsChatLoading(true);

    try {
      const response = await api.askAgent({
        question: text,
        product_title: analysisProduct?.name || text,
        model,
        tier: 'all'
      });

      const aiText = response.answer || response.recommendation || (language === 'ar' ? 'تم فحص استفسارك بنجاح.' : 'Audit complete.');

      const aiMessage: ChatMessage = {
        id: 'msg-ai-' + Date.now(),
        sender: 'ai',
        role: 'assistant',
        text: aiText,
        content: aiText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        model_name: response.model_name || `Honest AI (${model})`,
        confidence: response.confidence || 95,
        is_recommendation: response.is_recommendation,
        has_verified_match: response.has_verified_match ?? response.deep_search?.has_verified_product ?? true,
        material_verdict: response.material_verdict,
        price_matrix: response.price_matrix,
        recommendation: response.recommendation
      };

      setThreads((prev) =>
        prev.map((t) => {
          if (t.id === targetThreadId) {
            return {
              ...t,
              messages: [...t.messages, aiMessage]
            };
          }
          return t;
        })
      );
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: 'msg-err-' + Date.now(),
        sender: 'ai',
        role: 'assistant',
        text: err?.message || 'Error communicating with Honest AI backend.',
        content: err?.message || 'Error communicating with Honest AI backend.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        error: true
      };

      setThreads((prev) =>
        prev.map((t) => {
          if (t.id === targetThreadId) {
            return {
              ...t,
              messages: [...t.messages, errorMessage]
            };
          }
          return t;
        })
      );
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleAskQuestionFromReport = (questionPrompt: string) => {
    setChatPrompt(questionPrompt);
    navigate('assistant');
  };

  const handleClearAllData = () => {
    setSaved([]);
    setHistory([]);
    setRecord(null);
    setThreads([]);
    setActiveThreadId(null);
    localStorage.removeItem('honest_saved_products');
    localStorage.removeItem('honest_analysis_history');
    localStorage.removeItem('honest_chat_threads');
    localStorage.removeItem('honest_upvoted_reviews');
  };

  return (
    <Shell
      page={page}
      onNavigate={navigate}
      user={user}
      savedCount={saved.length}
      isOnline={isOnline}
      toast={toast}
      setToast={setToast}
      onOpenAccount={() => setAccountOpen(true)}
    >
      {/* Route Views with Code-Splitting Suspense Boundary */}
      <Suspense
        fallback={
          <div className="page-loading-skeleton" role="status" aria-live="polite">
            <span className="mono-metric">
              {language === 'ar' ? 'جارٍ تحميل وحدة الفحص الجنائي…' : 'Loading forensic intelligence module…'}
            </span>
          </div>
        }
      >
        {page === 'dashboard' && (
          <Dashboard
            onSelectProduct={handleSelectProduct}
            onNavigate={navigate}
            saved={saved}
            onToggleSave={handleToggleSave}
            history={history}
            onSelectRecord={handleSelectRecord}
          />
        )}

        {page === 'analysis' && (
          <Analysis
            initialProduct={analysisProduct}
            record={record}
            onRecordChange={handleRecordChange}
            saved={saved}
            onToggleSave={handleToggleSave}
            onAskQuestion={handleAskQuestionFromReport}
            setToast={setToast}
            activeSubTab="overview"
          />
        )}

        {page === 'studio' && (
          <Analysis
            initialProduct={analysisProduct}
            record={record}
            onRecordChange={handleRecordChange}
            saved={saved}
            onToggleSave={handleToggleSave}
            onAskQuestion={handleAskQuestionFromReport}
            setToast={setToast}
            activeSubTab="reality"
          />
        )}

        {page === 'compare' && (
          <Analysis
            initialProduct={analysisProduct}
            record={record}
            onRecordChange={handleRecordChange}
            saved={saved}
            onToggleSave={handleToggleSave}
            onAskQuestion={handleAskQuestionFromReport}
            setToast={setToast}
            activeSubTab="compare"
          />
        )}

        {page === 'assistant' && (
          <Assistant
            threads={threads}
            activeThreadId={activeThreadId}
            onSelectThread={setActiveThreadId}
            onNewThread={handleNewThread}
            onDeleteThread={handleDeleteThread}
            onSendMessage={handleSendMessage}
            isLoading={isChatLoading}
            productContext={analysisProduct}
            setToast={setToast}
            initialPrompt={chatPrompt}
            onClearPrompt={() => setChatPrompt('')}
          />
        )}

        {page === 'saved' && (
          <Saved
            saved={saved}
            onToggleSave={handleToggleSave}
            onSelectProduct={handleSelectProduct}
            onNavigateToDashboard={() => navigate('dashboard')}
          />
        )}

        {page === 'reviews' && (
          <Community
            user={user}
            defaultProductName={analysisProduct?.name}
            setToast={setToast}
          />
        )}

        {(page === 'settings' || page === 'extension') && (
          <Settings
            user={user}
            onOpenAccount={() => setAccountOpen(true)}
            onClearAllData={handleClearAllData}
            setToast={setToast}
          />
        )}

        {page === 'preview' && (
          <PreviewPage
            onBackToChat={() => navigate('dashboard')}
            currentLang={language}
          />
        )}
      </Suspense>

      {accountOpen && (
        <AccountDialog
          user={user}
          onUserChange={setUser}
          setToast={setToast}
          onClose={() => setAccountOpen(false)}
        />
      )}
    </Shell>
  );
}

export function App() {
  return (
    <PreferencesProvider>
      <MainApp />
    </PreferencesProvider>
  );
}
export default App;
