#include "AssemblyShadowTerminalExecution.h"
#include <iostream>
namespace p=il2cpp::vm::assembly_shadow_terminal;
int main() {
    // Requirement-derived truth table: states 8/9 always poisoned; durable
    // failure poisons an enabled transaction, never disabled state 0.
    // A diagnostic exception requires BOTH native construction scope AND
    // independently verified physical fixed constructor identity.
    int checks=0, failures=0;
    for (int state=0; state<=9; ++state) {
        for (int durable=0; durable<=1; ++durable) {
            const bool terminal=(state==8 || state==9 || (state>=1 && durable));
            ++checks;
            if (p::TerminalForBusiness(state,durable)!=terminal) ++failures;
            for (int scope=0; scope<=1; ++scope) {
                for (int ctor=0; ctor<=1; ++ctor) {
                    const bool allow_fixed=(scope==1 && ctor==1);
                    const bool reject=terminal && !allow_fixed;
                    ++checks;
                    if (p::RejectMethod(state,durable,scope,ctor)!=reject) {
                        ++failures;
                        std::cerr<<"mismatch state="<<state<<" durable="<<durable
                                 <<" scope="<<scope<<" fixedCtor="<<ctor<<"\n";
                    }
                }
            }
        }
    }
    std::cout<<"checks="<<checks<<" failures="<<failures<<"\n";
    return failures ? 1 : 0;
}
